import ezdxf
import subprocess
from ezdxf import bbox
import lxml.etree
from datetime import timedelta
import time
import copy
import os
import sys

startup = time.time()


class LegendDesc:

    def __init__(self, label, x1, y1, x2, y2):
        self.label = label
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2


def log(msg):
    dt = timedelta(seconds=time.time() - startup)
    print("[{}] {}".format(dt, msg))


def svg_to_dxf(name):
    log("Flatten SVG")
    subprocess.run(["inkscape", "{}.svg".format(name), "--export-text-to-path", "--export-type=svg", "--export-filename=tmp/flat.svg"])
    subprocess.run(["inkscape", "tmp/flat.svg", "--export-plain-svg", "--export-filename=tmp/flat2.svg"])

    log("Remove unneeded")
    svg = lxml.etree.parse("tmp/flat2.svg")
    for e in svg.findall(".//{http://www.w3.org/2000/svg}path"):
        style = e.get("style")
        if style is None:
            continue
        if "fill:#999999" in style or "fill:#cccccc" in style:
            e.getparent().remove(e)
        # if "fill:#cccccc" in style:
        #     e.getparent().remove(e)
    svg.write("tmp/with_border.svg")
    for e in svg.findall(".//{http://www.w3.org/2000/svg}path"):
        style = e.get("style")
        if style is None:
            continue
        if "fill:#b3b3b3" in style:
            e.getparent().remove(e)
    svg.write("tmp/no_border.svg")

    log("SVG=>DXF")
    subprocess.run(["/usr/bin/python3", "/usr/share/inkscape/extensions/dxf_outlines.py", "--layer_option", "visible", "--units", "1/14.265209944751382",
        "--POLY", "true", "--output", "tmp/export_border.dxf", "tmp/with_border.svg"])
    subprocess.run(["/usr/bin/python3", "/usr/share/inkscape/extensions/dxf_outlines.py", "--layer_option", "visible", "--units", "1/14.265209944751382",
        "--POLY", "true", "--output", "tmp/export_noborder.dxf", "tmp/no_border.svg"])


def _delete_entities_outside(msp, desc):
    delete_entities = []
    for e in msp:
        keep = False
        bounding_box = bbox.extents([e])
        if bounding_box.extmin is not None:
            x1, y1, z1 = bounding_box.extmin
            x2, y2, z2 = bounding_box.extmax
            if x1 >= desc.x1 and y1 >= desc.y1 and x2 <= desc.x2 and y2 <= desc.y2:
                keep = True
        if not keep:
            delete_entities.append(e)
    for e in delete_entities:
        msp.delete_entity(e)


def _process_one(desc, export_border, export_noborder):
    log("Processing {}".format(desc.label))
    msp = export_border.modelspace()
    _delete_entities_outside(msp, desc)

    bounding_box = bbox.extents(msp)
    dx = -(bounding_box.extmin[0] + bounding_box.extmax[0]) / 2
    dy = -(bounding_box.extmin[1] + bounding_box.extmax[1]) / 2

    msp = export_noborder.modelspace()
    _delete_entities_outside(msp, desc)

    for e in msp:
        e.translate(dx, dy, 0)
    export_noborder.saveas("tmp/legend_{}.dxf".format(desc.label))


def process_one(*args, **kwargs):
    pid = os.fork()
    if pid == 0:
        _process_one(*args, **kwargs)
        sys.exit(0)
    else:
        os.waitpid(pid, 0)

L = LegendDesc

LEGENDS = {
    "Legends2l_base": [
        # line 1
        L("shift_icon_text_1.75u", 2, 271, 34, 288),
        L("control_1.75u", 34, 271, 67, 288),
        L("super_1.5u", 87, 271, 114, 288),

        # line 2
        L("ctrl_icon_1.25u", 2, 252, 23, 269),
        L("super_icon_1.25u", 23, 252, 48, 269),
        L("alt_icon_1.25u", 48, 252, 73, 269),
        L("shift_1.25u", 73, 252, 96, 269),
        L("menu_1.25u", 120, 252, 144, 269),
        L("ctrl_1u", 168, 252, 187, 269),
        L("alt_1u", 187, 252, 206, 269),
        L("numpad_star", 206, 252, 225, 269),
        L("win_1u", 244, 252, 262, 269),

        # line 3
        L("ctrl_icon_1.5u", 2, 232, 28, 249),
        L("super_icon_1u", 28, 232, 47, 249),
        L("alt_icon_1.5u", 47, 232, 76, 249),
        L("shift_1.5u", 76, 232, 105, 249),
        L("caps_lock_1.75u", 154, 232, 186, 249),
        L("enter_2.25u", 222, 232, 262, 249),
        L("win_1.25u", 262, 232, 287, 249),

        # line 4
        L("shift_2.25u", 2, 214, 43, 230),
        L("shift_2.75u", 43, 214, 95, 230),
        L("iso_angle_brackets", 95, 214, 114, 230),
        L("bs_1u", 114, 214, 133, 230),
        L("print", 153, 214, 172, 230),
        L("scroll", 172, 214, 191, 230),
        L("pause", 191, 214, 211, 230),
        L("num", 211, 214, 229, 230),
        L("numpad_div", 229, 214, 250, 230),
        L("numpad_mul", 250, 214, 268, 230),
        L("numpad_minus", 268, 214, 286, 230),

        # line 5
        L("shift_icon_1.75u", 2, 194, 33, 211),
        L("code_1.25u", 33, 194, 58, 211),
        L("backspace_2u", 58, 194, 95, 211),
        L("numpad_slash", 95, 194, 114, 211),
        L("insert", 154, 194, 172, 211),
        L("home", 172, 194, 192, 211),
        L("pgup", 192, 194, 211, 211),
        L("numpad_7", 211, 194, 230, 211),
        L("numpad_8", 230, 194, 249, 211),
        L("numpad_9", 249, 194, 268, 211),

        # line 6
        L("system_1.25u", 34, 175, 57, 192),
        L("sys", 57, 175, 77, 192),
        L("code", 77, 175, 95, 192),
        L("delete", 155, 175, 173, 192),
        L("end", 173, 175, 190, 192),
        L("pgdn", 190, 175, 210, 192),
        L("numpad_4", 210, 175, 230, 192),
        L("numpad_5", 230, 175, 250, 192),
        L("numpad_6", 250, 175, 270, 192),

        # line 7
        L("iso_grave", 2, 156, 19, 173),
        L("iso_2", 19, 156, 38, 173),
        L("iso_3", 38, 156, 57, 173),
        L("fn", 57, 156, 77, 173),
        L("tab_1.5u", 105, 156, 133, 173),
        L("esc_icon", 155, 156, 172, 173),
        L("up", 172, 156, 190, 173),
        L("numpad_plus", 190, 156, 211, 173),
        L("numpad_1", 211, 156, 230, 173),
        L("numpad_2", 230, 156, 249, 173),
        L("numpad_3", 249, 156, 267, 173),

        # line 8
        L("shift_icon_1.25u", 1, 137, 24, 154),
        L("iso_backslash", 24, 137, 43, 154),
        L("iso_quote", 43, 137, 61, 154),
        L("iso_hash", 61, 137, 80, 154),
        L("backspace_icon_1.5u", 107, 137, 133, 154),
        L("left", 154, 137, 173, 154),
        L("down", 173, 137, 192, 154),
        L("right", 192, 137, 211, 154),
        L("numpad_0_2u", 211, 137, 249, 154),
        L("numpad_dot", 249, 137, 268, 154),

        # line 9
        L("esc", 2, 118, 19, 135),
        L("f1", 19, 118, 38, 135),
        L("f2", 38, 118, 58, 135),
        L("f3", 58, 118, 76, 135),
        L("f4", 76, 118, 95, 135),
        L("f5", 95, 118, 115, 135),
        L("f6", 115, 118, 134, 135),
        L("f7", 134, 118, 153, 135),
        L("f8", 153, 118, 172, 135),
        L("f9", 172, 118, 192, 135),
        L("f10", 192, 118, 212, 135),
        L("f11", 212, 118, 229, 135),
        L("f12", 229, 118, 248, 135),
        L("numpad_0", 248, 118, 269, 135),
        L("numpad_00", 269, 118, 286, 135),

        # line 10
        L("grave", 2, 98, 19, 116),
        L("numrow_1", 19, 98, 38, 116),
        L("numrow_2", 38, 98, 57, 116),
        L("numrow_3", 57, 98, 78, 116),
        L("numrow_4", 78, 98, 96, 116),
        L("numrow_5", 96, 98, 116, 116),
        L("numrow_6", 116, 98, 134, 116),
        L("numrow_7", 134, 98, 153, 116),
        L("numrow_8", 153, 98, 171, 116),
        L("numrow_9", 171, 98, 192, 116),
        L("numrow_0", 192, 98, 211, 116),
        L("numrow_minus", 211, 98, 231, 116),
        L("numrow_eq", 231, 98, 248, 116),
        L("backspace_icon_2u", 248, 98, 287, 116),

        # line 11
        L("tab_icon_1.5u", 1, 79, 29, 97),
        L("q", 29, 79, 48, 97),
        L("w", 48, 79, 67, 97),
        L("e", 67, 79, 87, 97),
        L("r", 87, 79, 106, 97),
        L("t", 106, 79, 124, 97),
        L("y", 124, 79, 143, 97),
        L("u", 143, 79, 163, 97),
        L("i", 163, 79, 182, 97),
        L("o", 182, 79, 202, 97),
        L("p", 202, 79, 220, 97),
        L("bracket_open", 220, 79, 240, 97),
        L("bracket_close", 240, 79, 258, 97),
        L("backslash_1.5u", 258, 79, 286, 97),

        # line 12
        L("caps_icon_1.75u", 2, 60, 33, 77),
        L("a", 33, 60, 53, 77),
        L("s", 53, 60, 72, 77),
        L("d", 72, 60, 91, 77),
        L("f", 91, 60, 109, 77),
        L("g", 109, 60, 129, 77),
        L("h", 129, 60, 148, 77),
        L("j", 148, 60, 168, 77),
        L("k", 168, 60, 187, 77),
        L("l", 187, 60, 205, 77),
        L("semicolon", 205, 60, 225, 77),
        L("quote", 225, 60, 243, 77),
        L("enter_icon_2.25u", 243, 60, 287, 77),

        # line 13
        L("shift_icon_2.25u", 1, 41, 43, 58),
        L("z", 43, 41, 62, 58),
        L("x", 62, 41, 81, 58),
        L("c", 81, 41, 100, 58),
        L("v", 100, 41, 119, 58),
        L("b", 119, 41, 139, 58),
        L("n", 139, 41, 158, 58),
        L("m", 158, 41, 176, 58),
        L("comma", 176, 41, 196, 58),
        L("dot", 196, 41, 216, 58),
        L("slash", 216, 41, 234, 58),
        L("shift_icon_2.75u", 234, 41, 287, 58),

        # line 14
        L("ctrl_1.25u", 2, 21, 24, 39),
        L("super_1.25u", 24, 21, 48, 39),
        L("alt_1.25u", 48, 21, 72, 39),
        L("fn_1.25u", 240, 21, 263, 39),

        # line 15
        L("ctrl_1.5u", 2, 3, 28, 20),
        L("super_1u", 28, 3, 48, 20),
        L("alt_1.5u", 48, 3, 75, 20),

        # special
        L("numpad_plus_2uvert", 270, 175, 286, 211),
        L("numpad_enter_icon_2uvert", 269, 136, 286, 173),
        L("numpad_enter_2uvert", 136, 136, 152, 173),
        L("iso_enter", 261, 252, 285, 288),
        L("iso_enter_icon", 79, 137, 104, 173),
        L("stepped_caps", 189, 233, 209, 249),
        L("stepped_caps_icon", 2, 175, 22, 192),
    ],
    "Legends2l_jp": [
        L("jp_iso_grave", 2, 156, 19, 173),
        L("jp_iso_2", 19, 156, 38, 173),
        L("jp_iso_3", 38, 156, 57, 173),

        L("jp_iso_backslash", 24, 137, 43, 154),

        L("jp_grave", 2, 98, 19, 116),
        L("jp_numrow_1", 19, 98, 38, 116),
        L("jp_numrow_2", 38, 98, 57, 116),
        L("jp_numrow_3", 57, 98, 78, 116),
        L("jp_numrow_4", 78, 98, 96, 116),
        L("jp_numrow_5", 96, 98, 116, 116),
        L("jp_numrow_6", 116, 98, 134, 116),
        L("jp_numrow_7", 134, 98, 153, 116),
        L("jp_numrow_8", 153, 98, 171, 116),
        L("jp_numrow_9", 171, 98, 192, 116),
        L("jp_numrow_0", 192, 98, 211, 116),
        L("jp_numrow_minus", 211, 98, 231, 116),
        L("jp_numrow_eq", 231, 98, 248, 116),

        L("jp_q", 29, 79, 48, 97),
        L("jp_w", 48, 79, 67, 97),
        L("jp_e", 67, 79, 87, 97),
        L("jp_r", 87, 79, 106, 97),
        L("jp_t", 106, 79, 124, 97),
        L("jp_y", 124, 79, 143, 97),
        L("jp_u", 143, 79, 163, 97),
        L("jp_i", 163, 79, 182, 97),
        L("jp_o", 182, 79, 202, 97),
        L("jp_p", 202, 79, 220, 97),
        L("jp_bracket_open", 220, 79, 240, 97),
        L("jp_bracket_close", 240, 79, 258, 97),
        L("jp_backslash_1.5u", 258, 79, 286, 97),

        L("jp_a", 33, 60, 53, 77),
        L("jp_s", 53, 60, 72, 77),
        L("jp_d", 72, 60, 91, 77),
        L("jp_f", 91, 60, 109, 77),
        L("jp_g", 109, 60, 129, 77),
        L("jp_h", 129, 60, 148, 77),
        L("jp_j", 148, 60, 168, 77),
        L("jp_k", 168, 60, 187, 77),
        L("jp_l", 187, 60, 205, 77),
        L("jp_semicolon", 205, 60, 225, 77),
        L("jp_quote", 225, 60, 243, 77),

        L("jp_z", 43, 41, 62, 58),
        L("jp_x", 62, 41, 81, 58),
        L("jp_c", 81, 41, 100, 58),
        L("jp_v", 100, 41, 119, 58),
        L("jp_b", 119, 41, 139, 58),
        L("jp_n", 139, 41, 158, 58),
        L("jp_m", 158, 41, 176, 58),
        L("jp_comma", 176, 41, 196, 58),
        L("jp_dot", 196, 41, 216, 58),
        L("jp_slash", 216, 41, 234, 58),
    ],
    "Legends2l_extra1": [
        L("f13", 19, 118, 38, 135),
        L("f14", 38, 118, 58, 135),
        L("f15", 58, 118, 76, 135),
        L("f16", 76, 118, 95, 135),
        L("f17", 95, 118, 115, 135),
        L("f18", 115, 118, 134, 135),
        L("f19", 134, 118, 153, 135),
        L("f20", 153, 118, 172, 135),
        L("f21", 172, 118, 192, 135),
        L("f22", 192, 118, 212, 135),
        L("f23", 212, 118, 229, 135),
        L("f24", 229, 118, 248, 135),
        L("stepped_ctrl", 189, 233, 209, 249),
    ],
    "Legends2l_extra2": [
        L("win_icon_1.25u", 23, 252, 48, 269),
        L("win_icon_1u", 28, 232, 47, 249),
    ],
    "Legends2l_extra3": [
        L("stepped_control", 189, 233, 209, 249),
        L("m1", 19, 118, 38, 135),
        L("m2", 38, 118, 58, 135),
        L("m3", 58, 118, 76, 135),
        L("m4", 76, 118, 95, 135),
        L("m5", 95, 118, 115, 135),
        L("m6", 115, 118, 134, 135),
        L("m7", 134, 118, 153, 135),
        L("m8", 153, 118, 172, 135),
        L("m9", 172, 118, 192, 135),
        L("m10", 192, 118, 212, 135),
        L("m11", 212, 118, 229, 135),
        L("m12", 229, 118, 248, 135),
    ],
}

L = None


def main():
    for name, legends in LEGENDS.items():
        log("-" * 80)
        log("Now working on: {}".format(name))
        log("-" * 80)
        svg_to_dxf(name)
        log("Fully converted")

        log("Read DXF")
        export_border = ezdxf.readfile("tmp/export_border.dxf")
        export_noborder = ezdxf.readfile("tmp/export_noborder.dxf")
        log("OK!")

        log("-" * 80)
        for legend in legends:
            process_one(legend, export_border, export_noborder)
        log("-" * 80)


if __name__ == "__main__":
    main()

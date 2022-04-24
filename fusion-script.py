import adsk.core, adsk.fusion, traceback

def find_keycap_surface(body):
    points = adsk.core.ObjectCollection.create()
    faces = body.parentComponent.findBRepUsingRay(adsk.core.Point3D.create(0, -0.65, 0), adsk.core.Vector3D.create(0, 0, -1), 1, -1.0, True, points)

    for face in faces:
        # print(face, face.appearance.name)
        if "Green" in face.appearance.name:
            return face


def is_directly_connected(first, second):
    first_edges = set()
    for edge in first.edges:
        first_edges.add(edge.tempId)
    second_edges = set()
    for edge in second.edges:
        second_edges.add(edge.tempId)
    return len(first_edges & second_edges) > 0


def recursively_color_legends(current, processed, coloring_legend, legend_color):
    processed.add(current.tempId)
    inner_faces = []
    for face in current.tangentiallyConnectedFaces:
        if face.tempId in processed or "Green" not in face.appearance.name or not is_directly_connected(face, current):
            continue
        if coloring_legend:
            face.appearance = legend_color
        inner_faces.append(face)
    for face in inner_faces:
        recursively_color_legends(face, processed, not coloring_legend, legend_color)


def process_one(name):
    legends = name.split("+")
    legend_colors = ["Paint - Enamel Glossy (Red)", "Paint - Enamel Glossy (Dark Grey)"]

    for idx, legend in enumerate(legends):
        # TODO: don't hardcode?
        dxf_filename = "C:\\Users\\xyz\\Documents\\keyboard\\keycaps-new\\tmp\\legend_{}.dxf".format(legend)

        app = adsk.core.Application.get()
        importManager = app.importManager

        design = adsk.fusion.Design.cast(app.activeProduct)

        # Get the root component of the active design
        rootComp = design.rootComponent

        body = rootComp.bRepBodies.item(0)
        best_face = find_keycap_surface(body)

        # Get dxf import options
        # dxfFileName = "C:\\Users\\xyz\\Documents\\keyboard\\keycaps-new\\legends2\\legend_E.dxf"
        dxfFileName = dxf_filename
        dxfOptions = importManager.createDXF2DImportOptions(dxfFileName, rootComp.xYConstructionPlane)
        dxfOptions.isViewFit = False
        # dxfOptions.position = adsk.core.Point2D.create(-0.9064, -83.4658)
        # dxfOptions.position = adsk.core.Point2D.create(-0.01, -0.20)
        
        # Import dxf file to root component
        importManager.importToTarget(dxfOptions, rootComp)

        sketch = dxfOptions.results.item(0)
        
        # Get SplitFaceFetures
        splitFaceFeatures = rootComp.features.splitFaceFeatures
        
        # Set faces to split
        facesCol = adsk.core.ObjectCollection.create()
        facesCol.add(best_face)

        curves = adsk.core.ObjectCollection.create()
        for x in range(sketch.sketchCurves.count):
            curves.add(sketch.sketchCurves.item(x))
        
        # Create a split face feature of surface intersection split type
        splitFaceInput = splitFaceFeatures.createInput(facesCol, curves, True)
        splitFaceFeatures.add(splitFaceInput)

        # color the legend
        lib = app.materialLibraries.itemByName("Fusion 360 Appearance Library")
        green = lib.appearances.itemByName("Paint - Enamel Glossy (Green)")
        legend_color = lib.appearances.itemByName(legend_colors[idx])
        yellow = lib.appearances.itemByName("Paint - Enamel Glossy (Yellow)")
        best_face = find_keycap_surface(body)
        # best_face.appearance = yellow
        recursively_color_legends(best_face, set(), True, legend_color)
        sketch.isVisible = False

    # dot/barred are yellow colored in template to make sure they don't get recolored into red legend color
    # so now change them to green
    for face in body.faces:
        if "Yellow" in face.appearance.name:
            face.appearance = green


def find_template(template_folder, model):
    for f in template_folder.dataFiles:
        if f.name == model:
            return f


MODELS = {
    "1u": ["R0_1u", "R1_1u", "R2_1u", "R3_1u", "R3_1u_dot", "R3_1u_barred", "R3_1u_deep", "R4_1u", "R5_1u"],
    "1u_simple": ["R0_1u", "R1_1u", "R2_1u", "R3_1u", "R4_1u", "R5_1u"],
    "1u_nobar": ["R0_1u", "R1_1u", "R2_1u", "R3_1u", "R3_1u_dot", "R3_1u_deep", "R4_1u", "R5_1u"],
    "1.25u": ["R3_1.25u", "R4_1.25u", "R5_1.25u"],
    "1.5u": ["R1_1.5u", "R2_1.5u", "R3_1.5u", "R4_1.5u", "R5_1.5u"],
    "1.75u": ["R2_1.75u", "R3_1.75u", "R4_1.75u"],
    "2u": ["R1_2u", "R2_2u", "R4_2u", "R5_2u"],
    "2.25u": ["R3_2.25u", "R4_2.25u"],
    "2.75u": ["R4_2.75u"],
    "iso_enter": ["R2-R3_ISO_Enter"],  # , "R2-R3_Thin_ISO_Enter"], - legends are broken for the thin version anyway
    "stepped_caps": ["R3_1.75u_Stepped"],
    "vertical_2u": ["R2-R3_1u", "R4-R4_1u"],
}

LEGENDS = [
    ("shift_icon_text_1.75u", "1.75u"), 
    ("control_1.75u", "1.75u"), 
    # ("f13", "1u_simple"), 
    ("super_1.5u", "1.5u"), 
    ("ctrl_icon_1.25u", "1.25u"), 
    ("super_icon_1.25u", "1.25u"), 
    ("alt_icon_1.25u", "1.25u"), 
    ("shift_1.25u", "1.25u"), 
    ("menu_1.25u", "1.25u"), 
    ("ctrl_1u", "1u_simple"), 
    ("alt_1u", "1u_simple"), 
    ("numpad_star", "1u_simple"), 
    ("win_1u", "1u_simple"), 
    ("ctrl_icon_1.5u", "1.5u"), 
    ("super_icon_1u", "1u_simple"), 
    ("alt_icon_1.5u", "1.5u"), 
    ("shift_1.5u", "1.5u"), 
    ("caps_lock_1.75u", "1.75u"), 
    ("enter_2.25u", "2.25u"), 
    ("win_1.25u", "1.25u"), 
    ("shift_2.25u", "2.25u"), 
    ("shift_2.75u", "2.75u"), 
    ("iso_angle_brackets", "1u_simple"), 
    ("bs_1u", "1u_simple"), 
    ("print", "1u_simple"), 
    ("scroll", "1u_simple"), 
    ("pause", "1u_simple"), 
    ("num", "1u_simple"), 
    ("numpad_div", "1u_simple"), 
    ("numpad_mul", "1u_simple"), 
    ("numpad_minus", "1u_simple"), 
    ("shift_icon_1.75u", "1.75u"), 
    ("code_1.25u", "1.25u"), 
    ("backspace_2u", "2u"), 
    ("numpad_slash", "1u_simple"), 
    ("insert", "1u_simple"), 
    ("home", "1u_simple"), 
    ("pgup", "1u_simple"), 
    ("numpad_7", "1u"), 
    ("numpad_8", "1u"), 
    ("numpad_9", "1u"), 
    ("system_1.25u", "1.25u"), 
    ("sys", "1u_simple"), 
    ("code", "1u_simple"), 
    ("delete", "1u_simple"), 
    ("end", "1u_simple"), 
    ("pgdn", "1u_simple"), 
    ("numpad_4", "1u"), 
    ("numpad_5", "1u"), 
    ("numpad_6", "1u"), 
    ("iso_grave", "1u_simple"), 
    ("iso_2", "1u_simple"), 
    ("iso_3", "1u_simple"), 
    ("fn", "1u_simple"), 
    ("tab_1.5u", "1.5u"), 
    ("up", "1u_simple"), 
    ("numpad_plus", "1u_simple"), 
    ("numpad_1", "1u"), 
    ("numpad_2", "1u"), 
    ("numpad_3", "1u"), 
    ("shift_icon_1.25u", "1.25u"), 
    ("iso_backslash", "1u_simple"), 
    ("iso_quote", "1u_simple"), 
    ("iso_hash", "1u_simple"), 
    ("backspace_icon_1.5u", "1.5u"), 
    ("left", "1u_simple"), 
    ("down", "1u_simple"), 
    ("right", "1u_simple"), 
    ("numpad_0_2u", "2u"), 
    ("numpad_dot", "1u_simple"), 
    ("esc", "1u_simple"), 
    ("f1", "1u_simple"), 
    ("f2", "1u_simple"), 
    ("f3", "1u_simple"), 
    ("f4", "1u_simple"), 
    ("f5", "1u_simple"), 
    ("f6", "1u_simple"), 
    ("f7", "1u_simple"), 
    ("f8", "1u_simple"), 
    ("f9", "1u_simple"), 
    ("f10", "1u_simple"), 
    ("f11", "1u_simple"), 
    ("f12", "1u_simple"), 
    ("numpad_0", "1u"), 
    ("numpad_00", "1u"), 
    ("grave", "1u_simple"), 
    ("numrow_1", "1u_simple"), 
    ("numrow_2", "1u_simple"), 
    ("numrow_3", "1u_simple"), 
    ("numrow_4", "1u_simple"), 
    ("numrow_5", "1u_simple"), 
    ("numrow_6", "1u_simple"), 
    ("numrow_7", "1u_simple"), 
    ("numrow_8", "1u_simple"), 
    ("numrow_9", "1u_simple"), 
    ("numrow_0", "1u_simple"), 
    ("numrow_minus", "1u_simple"), 
    ("numrow_eq", "1u_simple"), 
    ("backspace_icon_2u", "2u"), 
    ("tab_icon_1.5u", "1.5u"), 
    ("q", "1u"), 
    ("w", "1u"), 
    ("e", "1u"), 
    ("r", "1u"), 
    ("t", "1u"), 
    ("y", "1u"), 
    ("u", "1u"), 
    ("i", "1u"), 
    ("o", "1u"), 
    ("p", "1u"), 
    ("bracket_open", "1u_simple"), 
    ("bracket_close", "1u_simple"), 
    ("backslash_1.5u", "1.5u"), 
    ("caps_icon_1.75u", "1.75u"), 
    ("a", "1u"), 
    ("s", "1u"), 
    ("d", "1u"), 
    ("f", "1u"), 
    ("g", "1u"), 
    ("h", "1u"), 
    ("j", "1u"), 
    ("k", "1u"), 
    ("l", "1u"), 
    ("semicolon", "1u_simple"), 
    ("quote", "1u_simple"), 
    ("enter_icon_2.25u", "2.25u"), 
    ("shift_icon_2.25u", "2.25u"), 
    ("z", "1u"), 
    ("x", "1u"), 
    ("c", "1u"), 
    ("v", "1u"), 
    ("b", "1u"), 
    ("n", "1u"), 
    ("m", "1u"), 
    ("comma", "1u_simple"), 
    ("dot", "1u_simple"), 
    ("slash", "1u_simple"), 
    ("shift_icon_2.75u", "2.75u"), 
    ("ctrl_1.25u", "1.25u"), 
    ("super_1.25u", "1.25u"), 
    ("alt_1.25u", "1.25u"), 
    ("fn_1.25u", "1.25u"), 
    ("ctrl_1.5u", "1.5u"), 
    ("super_1u", "1u"), 
    ("alt_1.5u", "1.5u"), 

    # "esc_icon", "1u_simple", # - broken self-intersecting path error

    ("numpad_plus_2uvert", "vertical_2u"),
    ("numpad_enter_icon_2uvert", "vertical_2u"),
    ("numpad_enter_2uvert", "vertical_2u"),
    ("iso_enter", "iso_enter"),
    ("iso_enter_icon", "iso_enter"),
    ("stepped_caps", "stepped_caps"),
    ("stepped_caps_icon", "stepped_caps"),

    ("iso_grave+jp_iso_grave", "1u_nobar"),
    ("iso_2+jp_iso_2", "1u_nobar"),
    ("iso_3+jp_iso_3", "1u_nobar"),

    ("iso_backslash+jp_iso_backslash", "1u_nobar"),

    ("grave+jp_grave", "1u_nobar"),
    ("numrow_1+jp_numrow_1", "1u_nobar"),
    ("numrow_2+jp_numrow_2", "1u_nobar"),
    ("numrow_3+jp_numrow_3", "1u_nobar"),
    ("numrow_4+jp_numrow_4", "1u_nobar"),
    ("numrow_5+jp_numrow_5", "1u_nobar"),
    ("numrow_6+jp_numrow_6", "1u_nobar"),
    ("numrow_7+jp_numrow_7", "1u_nobar"),
    ("numrow_8+jp_numrow_8", "1u_nobar"),
    ("numrow_9+jp_numrow_9", "1u_nobar"),
    ("numrow_0+jp_numrow_0", "1u_nobar"),
    ("numrow_minus+jp_numrow_minus", "1u_nobar"),
    ("numrow_eq+jp_numrow_eq", "1u_nobar"),

    ("q+jp_q", "1u_nobar"),
    ("w+jp_w", "1u_nobar"),
    ("e+jp_e", "1u_nobar"),
    ("r+jp_r", "1u_nobar"),
    ("t+jp_t", "1u_nobar"),
    ("y+jp_y", "1u_nobar"),
    ("u+jp_u", "1u_nobar"),
    ("i+jp_i", "1u_nobar"),
    ("o+jp_o", "1u_nobar"),
    ("p+jp_p", "1u_nobar"),
    ("bracket_open+jp_bracket_open", "1u_nobar"),
    ("bracket_close+jp_bracket_close", "1u_nobar"),
    ("backslash_1.5u+jp_backslash_1.5u", "1.5u"),

    ("a+jp_a", "1u_nobar"),
    ("s+jp_s", "1u_nobar"),
    ("d+jp_d", "1u_nobar"),
    ("f+jp_f", "1u_nobar"),
    ("g+jp_g", "1u_nobar"),
    ("h+jp_h", "1u_nobar"),
    ("j+jp_j", "1u_nobar"),
    ("k+jp_k", "1u_nobar"),
    ("l+jp_l", "1u_nobar"),
    ("semicolon+jp_semicolon", "1u_nobar"),
    ("quote+jp_quote", "1u_nobar"),

    ("z+jp_z", "1u_nobar"),
    ("x+jp_x", "1u_nobar"),
    ("c+jp_c", "1u_nobar"),
    ("v+jp_v", "1u_nobar"),
    ("b+jp_b", "1u_nobar"),
    ("n+jp_n", "1u_nobar"),
    ("m+jp_m", "1u_nobar"),
    ("comma+jp_comma", "1u_nobar"),
    ("dot+jp_dot", "1u_nobar"),
    ("slash+jp_slash", "1u_nobar"),

    ("f13", "1u"),
    ("f14", "1u"),
    ("f15", "1u"),
    ("f16", "1u"),
    ("f17", "1u"),
    ("f18", "1u"),
    ("f19", "1u"),
    ("f20", "1u"),
    ("f21", "1u"),
    ("f22", "1u"),
    ("f23", "1u"),
    ("f24", "1u"),
    # ("win_icon_1u", "1u"),
    ("m1", "1u"),
    ("m2", "1u"),
    ("m3", "1u"),
    ("m4", "1u"),
    ("m5", "1u"),
    ("m6", "1u"),
    ("m7", "1u"),
    ("m8", "1u"),
    ("m9", "1u"),
    ("m10", "1u"),
    ("m11", "1u"),
    ("m12", "1u"),

    ("stepped_ctrl", "stepped_caps"),
    ("stepped_control", "stepped_caps"),
    # ("win_icon_1.25u", "1.25u"),
]

def get_dest_folder(folder, name):
    for x in folder.dataFolders:
        if x.name == name:
            return x
    return folder.dataFolders.add(name)


def counter(legends):
    count = 0
    for legend, size in legends:
        count += len(MODELS[size])
    return count


def run(context):
    # print(counter(LEGENDS1), counter(LEGENDS2), counter(LEGENDS3))
    # return

    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        split_legends = [[]]
        for it in LEGENDS:
            if counter(split_legends[-1] + [it]) <= 250:
                split_legends[-1].append(it)
            else:
                split_legends.append([it])

        lens = [counter(x) for x in split_legends]
        total = sum(lens)
        index, cancelled = ui.inputBox("Export part# - enter 0 to {}\n(total={}; {})".format(len(split_legends) - 1, total, ", ".join(str(x) for x in lens)),
            "Keycap generator", "")
        if cancelled:
            return
        index = int(index)

        for x in app.data.dataProjects:
            if x.name == "autokeycaps":
                dp = x
                break
        df = dp.rootFolder
        output_folder = "output{}".format(index)
        for folder in df.dataFolders:
            if folder.name == output_folder:
                raise RuntimeError("delete '{}' yourself!".format(output_folder))
            elif folder.name == "template":
                template_folder = folder
        output_folder = df.dataFolders.add(output_folder)

        for legend, size in split_legends[index]:
            for model in MODELS[size]:
                datafile = find_template(template_folder, model)
                doc = app.documents.open(datafile)
                doc.saveAs(legend, get_dest_folder(output_folder, model), "", "")
                process_one(legend)
                doc.save("")
                doc.close(True)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

bl_info = {
    "name": "Simple Boolean Cut",
    "author" : "bagusindrayana",
    "description" : "Simple plugin to add boolean modifier to object",
    'blender': (3, 3, 0),
    'version': (0, 1, 0),
    'category': 'General',
    'location': '3D View',
    'support': 'COMMUNITY',
    'warning': '',
    'doc_url': '',
    'tracker_url':'' 
}
import bpy  
from bpy.types import Panel, Operator

bpy.app.handlers.depsgraph_update_post.clear()

previous_objects = set([])
useBoolean = False
currentObject = None

class OBJECT_OT_AddAssetOperator(Operator):
    bl_idname = "object.add_asset_operator"
    bl_label = "Add Asset Operator"
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        global currentObject
        currentObject = context.active_object
        context.scene.asset_target_object = context.active_object
        return {'FINISHED'}

class SBC_AssetPanel(Panel):
    bl_label = "Simple Boolean Cut"
    bl_idname = "SBC_asset_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SimpleBC"
    
    def execute(self, context):
        global useBoolean,currentObject
        if scene.use_boolean_modifier is not None:
            useBoolean = scene.use_boolean_modifier
        return {'FINISHED'}

    def draw(self, context):
        global useBoolean,currentObject
        
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.prop(scene, "use_boolean_modifier",text="Use Boolean Cut")

        if scene.use_boolean_modifier:
            row = layout.row()
            row.prop_search(scene, "asset_target_object", context.scene, "objects", text="Target Object")
            row = layout.row()
            row.operator("object.add_asset_operator", text="Set Target")
            
        if context.scene.asset_target_object is not None:
            currentObject = context.scene.asset_target_object
        if scene.use_boolean_modifier is not None:
            useBoolean = scene.use_boolean_modifier
        if useBoolean:
            layout.row().label(text="List Boolean : ")
            if context.scene.asset_target_object is not None:
                for mod in context.scene.asset_target_object.modifiers:
                    _row = layout.row()
                    _row.label(text=mod.name)
            

def register():
    bpy.types.Scene.use_boolean_modifier = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.asset_target_object = bpy.props.PointerProperty(type=bpy.types.Object)
    
    bpy.utils.register_class(OBJECT_OT_AddAssetOperator)
    bpy.utils.register_class(SBC_AssetPanel)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_AddAssetOperator)
    bpy.utils.unregister_class(SBC_AssetPanel)
    del bpy.types.Scene.use_boolean_modifier
    del bpy.types.Scene.asset_target_object

def add_boolean_modifier(obj):
    global currentObject
    if currentObject != None:
        obj.display_type = "WIRE"
        selected_obj = currentObject
        bool_mod = selected_obj.modifiers.new(name=obj.name+" Boolean", type="BOOLEAN")
        bool_mod.object = obj
        bool_mod.operation = 'DIFFERENCE'
    
    

def new_object_added(scene):
    global previous_objects,useBoolean
    current_objects = set(bpy.data.objects)
    new_objects = current_objects - previous_objects
    previous_objects = current_objects
    if not new_objects:
        return
    for obj in new_objects:
        print("New object added: ", obj.name, type(obj))
        if useBoolean:
            add_boolean_modifier(obj)

bpy.app.handlers.depsgraph_update_post.append(new_object_added)

if __name__ == "__main__":
    register()

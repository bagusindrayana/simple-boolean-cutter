bl_info = {
    "name": "Simple Boolean Cutter",
    "author" : "bagusindrayana",
    "description" : "Simple plugin to add boolean modifier to object",
    "version": (0, 1, 1),
    "blender": (2, 80, 0),
    "category": 'General',
    'location': '3D View',
    'support': 'COMMUNITY',
    'warning': '',
    'doc_url': '',
    'tracker_url':'' 
}
import bpy  
from bpy.types import Panel, Operator
from bpy.app.handlers import persistent



class OBJECT_OT_AddAssetOperator(Operator):
    bl_idname = "object.add_asset_operator"
    bl_label = "Add Asset Operator"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        context.scene.asset_target_object = context.active_object
        bpy.context.scene.cursor.location = context.scene.asset_target_object.location
        return {'FINISHED'}

class OBJECT_OT_ApplyModifierOperator(Operator):
    bl_idname = "object.apply_modifier_operator"
    bl_label = "Apply Modifier Operator"
    bl_options = {'UNDO'}

    def execute(self, context):
        context.view_layer.objects.active = context.scene.asset_target_object
        for modifier in context.scene.asset_target_object.modifiers:
            try:
                if modifier and modifier.type == "BOOLEAN":
                    bpy.ops.object.modifier_apply({"active_object": context.scene.asset_target_object},modifier=modifier.name)
            except RuntimeError as ex:
                # print the error incase its important... but continue
                print(ex)
        _parent = bpy.data.collections.get("SimpleBC_Collections")
        if _parent:
            _child = _parent.children.get(context.scene.asset_target_object.name)
            if _child:
                for _obj in _child.objects:
                    bpy.data.objects.remove(_obj, do_unlink=True)
            
        return {'FINISHED'}

class SBC_AssetPanel(Panel):
    bl_label = "Simple Boolean Cut"
    bl_idname = "SBC_asset_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SimpleBC"
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.prop(scene, "use_boolean_modifier",text="Use Boolean Cut")


        if scene.use_boolean_modifier:
            row = layout.row()
            row.prop_search(scene, "asset_target_object", context.scene, "objects", text="Target Object")
            row = layout.row()
            row.operator("object.add_asset_operator", text="Set Target")
            row = layout.row()
            row.operator("object.apply_modifier_operator", text="Apply Boolean")
            
        if scene.use_boolean_modifier:
            layout.row().label(text="List Boolean : ")
            if context.scene.asset_target_object is not None:
                for mod in context.scene.asset_target_object.modifiers:
                    if mod.type == "BOOLEAN":
                        _row = layout.row()
                        _row.label(text=mod.name)
            

class ObjectList(bpy.types.PropertyGroup):
    object: bpy.props.PointerProperty(type=bpy.types.Object)

def register():
    bpy.app.handlers.depsgraph_update_post.clear()
    bpy.types.Scene.use_boolean_modifier = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.dynamic_target = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.asset_target_object = bpy.props.PointerProperty(type=bpy.types.Object)
    
    bpy.utils.register_class(OBJECT_OT_AddAssetOperator)
    bpy.utils.register_class(OBJECT_OT_ApplyModifierOperator)
    bpy.utils.register_class(SBC_AssetPanel)
    bpy.app.handlers.depsgraph_update_post.append(new_object_added)

    bpy.utils.register_class(ObjectList)
    bpy.types.Scene.previous_objects = bpy.props.CollectionProperty(type=ObjectList)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_AddAssetOperator)
    bpy.utils.unregister_class(OBJECT_OT_ApplyModifierOperator)
    bpy.utils.unregister_class(SBC_AssetPanel)
    del bpy.types.Scene.use_boolean_modifier
    del bpy.types.Scene.dynamic_target
    del bpy.types.Scene.asset_target_object
    del bpy.types.Scene.previous_objects
    bpy.app.handlers.depsgraph_update_post.remove(new_object_added)


def find_or_create_collection(collection_name):
    # Cari koleksi dengan nama yang diberikan
    collection = bpy.data.collections.get(collection_name)
    if collection:
        # Jika koleksi ditemukan, kembalikan koleksi tersebut
        return collection
    else:
        # Jika koleksi tidak ditemukan, buat koleksi baru dengan nama tersebut
        collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(collection)
        # Kembalikan koleksi baru yang dibuat
        return collection
    

def add_boolean_modifier(obj):
    coll_target = find_or_create_collection("SimpleBC_Collections")
    if bpy.context.scene.asset_target_object != None and bpy.context.scene.asset_target_object != obj:
        print("Add Modifier: ", obj.name, type(obj))
        obj.display_type = "WIRE"
        selected_obj = bpy.context.scene.asset_target_object
        bool_mod = selected_obj.modifiers.new(name=obj.name+" Boolean", type="BOOLEAN")
        bool_mod.object = obj
        bool_mod.operation = 'DIFFERENCE'
        _child = find_or_create_collection(selected_obj.name)
        
        # cek collection and remove duplicate outliner
        _cek = bpy.context.view_layer.layer_collection.collection.children.get(_child.name)
        if _cek:
            bpy.context.view_layer.layer_collection.collection.children.unlink(_child)
        
        
        a = bpy.context.view_layer.active_layer_collection.collection
        col = bpy.data.collections.get(a.name)
        if col:
            _cek1 = col.objects.get(obj.name)
            if _cek1:
                col.objects.unlink(obj)
        
        _cek3 = bpy.context.view_layer.layer_collection.collection.objects.get(obj.name)
        if _cek3:
            bpy.context.view_layer.layer_collection.collection.objects.unlink(obj)
        _child.objects.link(obj)
        _cek2 = coll_target.children.get(_child.name)
        if _cek2 == None:
            coll_target.children.link(_child)
    
    
# @persistent
def new_object_added(scene):
    if scene.asset_target_object == None:
        return
    if scene.use_boolean_modifier == None or scene.use_boolean_modifier == False:
        return
    current_objects = set(bpy.data.objects)
    _list_object = []
    for _ol in scene.previous_objects:
       _list_object.append(_ol.object)
    new_objects = current_objects - set(_list_object)
    
    _tmp_list_object = []
    for _co in current_objects:
        _new = scene.previous_objects.add()
        _new.object = _co
        #_tmp_list_object.append(_new)
   
    #bpy.context.scene.previous_objects.objects = _tmp_list_object
    if not new_objects:
        return
    for obj in new_objects:
        print("New object added: ", obj.name, type(obj))
        if scene.use_boolean_modifier:
            add_boolean_modifier(obj)


if __name__ == "__main__":
    register()
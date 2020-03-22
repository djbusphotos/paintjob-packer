import os, shutil, binascii, codecs, configparser

output_path = os.path.expanduser("~/Desktop/Paintjob Packer Output")

class Vehicle:
    def __init__(self, file_name, game):
        veh_ini = configparser.ConfigParser(allow_no_value = True)
        veh_ini.read("library/vehicles/{}/{}.ini".format(game, file_name))
        self.make = veh_ini["vehicle info"]["make"]
        self.model = veh_ini["vehicle info"]["model"]
        self.path = veh_ini["vehicle info"]["vehicle path"]
        self.alt_uvset = veh_ini["vehicle info"].getboolean("alt uvset")
        self.name = veh_ini["vehicle info"]["name"]
        self.trailer = veh_ini["vehicle info"].getboolean("trailer")
        self.mod = veh_ini["vehicle info"].getboolean("mod")
        self.mod_author = veh_ini["vehicle info"]["mod author"]
        self.mod_link = veh_ini["vehicle info"]["mod link"]
        self.uses_accessories = veh_ini["vehicle info"].getboolean("uses accessories")
        if self.uses_accessories:
            self.accessories = veh_ini["vehicle info"]["accessories"].split(",")
            self.acc_dict = {}
            for acc in self.accessories:
                if acc != "":
                    self.acc_dict[acc] = list(veh_ini[acc].keys())
        if self.trailer:
            self.separate_paintjobs = False
            self.type = "trailer_owned"
        else:
            self.separate_paintjobs = veh_ini["cabins"].getboolean("separate paintjobs")
            self.type = "truck"
            self.cabins = dict(veh_ini["cabins"].items())
            self.cabins.pop("separate paintjobs", None)



def make_folder(path):
    if not os.path.exists(output_path + "/" + path):
        os.makedirs(output_path + "/" + path)

def convert_string_to_hex(string_input):
    if isinstance(string_input, int):
        string_input = bytes([string_input])
    elif isinstance(string_input, str):
        string_input = string_input.encode()
    string_output = binascii.hexlify(string_input)
    string_output = string_output.decode()
    return string_output

def generate_tobj(path): # TODO: icon tobj?
    tobj_string = "010AB170000000000000000000000000000000000100020002000303030002020001000000010000"
    tobj_string += convert_string_to_hex(len(path))
    tobj_string += "00000000000000"
    tobj_string += convert_string_to_hex(path)
    tobj_file = codecs.decode(tobj_string, "hex_codec")
    return tobj_file



# loose files

def make_manifest_sii(mod_version, mod_name, mod_author):
    file = open(output_path + "/manifest.sii", "w")
    file.write("SiiNunit\n")
    file.write("{\n")
    file.write("mod_package: .package_name\n")
    file.write("{\n")
    file.write("    package_version:  \"{}\"\n".format(mod_version))
    file.write("    display_name:     \"{}\"\n".format(mod_name))
    file.write("    author:           \"{}\"\n".format(mod_author))
    file.write("\n")
    file.write("    category[]:       \"paint_job\"\n")
    file.write("\n")
    file.write("    icon:             \"mod_manager_image.jpg\"\n")
    file.write("    description_file: \"mod_manager_description.txt\"\n")
    file.write("}\n")
    file.write("}\n")
    file.close()

def copy_mod_manager_image():
    shutil.copyfile("library/placeholder files/mod_manager_image.jpg", output_path + "/mod_manager_image.jpg")

def make_description(truck_list, trailer_list, mod_list):
    file = open(output_path + "/mod_manager_description.txt", "w")
    if len(truck_list) + len(mod_list) > 0:
        file.write("Trucks supported:\n")
        for veh in truck_list:
            file.write(veh.name+"\n")
        for veh in mod_list:
            file.write("{}'s {}\n'".format(veh.mod_author, veh.name))
        file.write("\n")
    if len(trailer_list) > 0:
        file.write("Trailers supported:\n")
        for veh in trailer_list:
            file.write(veh.name+"\n")
    file.close()



# material folder

def make_material_folder():
    make_folder("material/ui/accessory/")

def copy_paintjob_icon(internal_name):
    shutil.copyfile("library/placeholder files/paintjob_icon.dds", output_path + "/material/ui/accessory/{}_icon.dds".format(internal_name))

def make_paintjob_icon_tobj(internal_name): # TODO: tobj like SCS paintjobs, makes a difference?
    file = open(output_path + "/material/ui/accessory/{}_icon.tobj".format(internal_name), "wb")
    file.write(generate_tobj("/material/ui/accessory/{}_icon.dds".format(internal_name)))
    file.close()

def make_paintjob_icon_mat(internal_name):
    file = open(output_path + "/material/ui/accessory/{}_icon.mat".format(internal_name), "w")
    file.write("material: \"ui\"\n")
    file.write("{\n")
    file.write("    texture:      \"{}_icon.tobj\"\n".format(internal_name))
    file.write("    texture_name: \"texture\"\n")
    file.write("}\n")
    file.close()



# def folder

def make_def_folder(veh):
    extra_path = ""
    if veh.uses_accessories:
        extra_path = "/accessory"
    make_folder("def/vehicle/{}/{}/paint_job{}".format(veh.type, veh.path, extra_path))

def make_def_sii(veh, paintjob_name, internal_name, cab_name = None, cab_size = None):
    file = open(output_path + "/def/vehicle/{}/{}/paint_job/{}.sii".format(veh.type, veh.path, paintjob_name), "w")
    file.write("SiiNunit\n")
    file.write("{\n")
    file.write("accessory_paint_job_data: {}.{}.paint_job\n".format(paintjob_name, veh.path))
    file.write("{\n")
    file.write("@include \"{}_settings.sui\"\n".format(internal_name))
    if internal_name != paintjob_name: # cabin handling: separate paintjobs
        file.write("    suitable_for[]: \"{}.{}.cabin\"\n".format(cab_name, veh.path))
        file.write("    paint_job_mask: \"/vehicle/truck/upgrade/paintjob/{}/{}_{}/cabin_{}.tobj\"\n".format(internal_name, veh.make, veh.model, cab_size))
    elif veh.type == "truck": # cabin handling: combined paintjobs
        file.write("    paint_job_mask: \"/vehicle/truck/upgrade/paintjob/{}/{}_{}/cabin.tobj\"\n".format(internal_name, veh.make, veh.model))
    elif veh.type == "trailer_owned":
        file.write("    paint_job_mask: \"/vehicle/trailer_owned/upgrade/paintjob/{}/{}_{}/base_colour.tobj\"\n".format(internal_name, veh.make, veh.model))
    file.close()

def make_settings_sui(veh, internal_name, ingame_name, ingame_price, unlock_level):
    file = open(output_path + "/def/vehicle/{}/{}/paint_job/{}_settings.sui" % (veh.type, veh.path, internal_name), "w")
    file.write("    name:     \"{}\"\n".format(ingame_name))
    file.write("    price:    {}\n".format(ingame_price))
    file.write("    unlock:   {}\n".format(unlock_level))
    file.write("    airbrush: true\n")
    file.write("    icon:     \"paintjob_icons/{}_icon\"\n".format(internal_name))
    if veh.alt_uvset:
        file.write("    alternate_uvset: true\n")
    file.close()

def make_accessory_sii(veh, internal_name, paintjob_name):
    file = open(output_path + "/def/vehicle/{}/{}/paint_job/accessory/{}.sii".format(veh.type, veh.path, paintjob_name), "w")
    file.write("SiiNunit\n")
    file.write("{\n")
    ovr_counter = 0
    for acc_name in veh.acc_dict:
        file.write("\n")
        file.write("simple_paint_job_data: .ovr{}\n".format(ovr_counter))
        file.write("{\n")
        file.write("    paint_job_mask: \"/vehicle/{}/upgrade/paintjob/{}/{}_{}/{}.tobj\"\n".format(veh.type, internal_name, veh.make, veh.model, acc_name))
        for acc in veh.acc_dict[acc]:
            file.write("    acc_list[]: \"{}\"\n".format(acc))
        ovr_counter += 1
    file.write("}\n")
    file.close()



# vehicle folder

def make_vehicle_folder(veh, internal_name):
    make_folder("vehicle/{}/upgrade/paintjob/{}/{}_{}" % (veh.type, internal_name, veh.make, veh.model))

def copy_main_dds(veh, internal_name, paintjob_name, using_unifier):
    if internal_name != paintjob_name:
        if using_unifier:
            shutil.copyfile("library/placeholder files/empty.dds", output_folder + "/vehicle/truck/upgrade/paintjob/{}/{}_{}/cabin_a.dds".format(internal_name, veh.make, veh.model))
        else:
            for cab_size in veh.cabins:
                shutil.copyfile("library/placeholder files/empty.dds", output_folder + "/vehicle/truck/upgrade/paintjob/{}/{}_{}/cabin_{}.dds".format(internal_name, veh.make, veh.model, cab_size))
    elif veh.type == "truck":
        shutil.copyfile("library/placeholder files/empty.dds", output_folder + "/vehicle/truck/upgrade/paintjob/{}/{}_{}/cabin.dds".format(internal_name, veh.make, veh.model))
    elif veh.type == "trailer_owned":
        shutil.copyfile("library/placeholder files/empty.dds", output_folder + "/vehicle/trailer_owned/upgrade/paintjob/{}/{}_{}/base_colour.dds".format(internal_name, veh.make, veh.model))

def copy_accessory_dds(veh, internal_name):
    for acc_name in veh.acc_dict:
        shutil.copyfile("library/placeholder files/empty.dds", output_folder + "/vehicle/{}/upgrade/paintjob/{}/{}_{}/{}.dds".format(veh.type, internal_name, veh.make, veh.model, acc_name))

def make_main_tobj(veh, internal_name, paintjob_name, using_unifier):
    if internal_name != paintjob_name:
        for cab_size in veh.cabins:
            file = open(output_folder + "/vehicle/truck/upgrade/paintjob/{}/{}_{}/cabin_{}.tobj".format(internal_name, veh.make, veh.model, cab_size), "wb")
            if using_unifier:
                file.write(generate_tobj("/vehicle/truck/upgrade/paintjob/{}/{}_{}/cabin_a.dds".format(internal_name, veh.make, veh.model, cab_size)))
            else:
                file.write(generate_tobj("/vehicle/truck/upgrade/paintjob/{}/{}_{}/cabin_{}.dds".format(internal_name, veh.make, veh.model, cab_size)))
            file.close()
    elif veh.type == "truck":
        file = open(output_folder + "/vehicle/truck/upgrade/paintjob/{}/{}_{}/cabin.tobj".format(internal_name, veh.make, veh.model), "wb")
        file.write(generate_tobj("/vehicle/truck/upgrade/paintjob/{}/{}_{}/cabin.dds".format(internal_name, veh.make, veh.model)))
        file.close()
    elif veh.type == "trailer_owned":
        file = open(output_folder + "/vehicle/trailer/upgrade/paintjob/{}/{}_{}/base_colour.tobj".format(internal_name, veh.make, veh.model), "wb")
        file.write(generate_tobj("/vehicle/trailer/upgrade/paintjob/{}/{}_{}/base_colour.dds".format(internal_name, veh.make, veh.model)))
        file.close()

def make_accessory_tobj(veh, internal_name):
    for acc_name in veh.acc_dict:
        file = open(output_folder + "/vehicle/{}/upgrade/paintjob/{}/{}_{}/{}.tobj".format(veh.type, internal_name, veh.make, veh.model, acc_name), "wb")
        file.write(generate_tobj("/vehicle/{}/upgrade/paintjob/{}/{}_{}/{}.dds".format(veh.type, internal_name, veh.make, veh.model, acc_name)))
        file.close()



# packer functions

def make_unifier_ini(pack, vehicles_to_add = None):
    uni_ini = configparser.ConfigParser()
    uni_ini.add_section("paintjobs")

    for pj in pack.paintjobs:
        uni_ini["paintjobs"][pj.int_name] = ""
        if pj.int_name not in list(uni_ini.keys()):
            uni_ini.add_section(pj.int_name)
        if vehicles_to_add == None:
            uni_vehicles = pj.vehicles
        else:
            uni_vehicles = vehicles_to_add

        for veh in uni_vehicles:
            if veh.separate_paintjobs:
                veh_name = veh.make+"_"+veh.model
                uni_ini[pj.int_name][veh_name] = ""
                if veh_name not in list(uni_ini.keys()):
                    uni_ini.add_section(veh_name)
                    uni_ini[veh_name]["path"] = veh.path
                    uni_ini[veh_name]["accessories"] = str(veh.uses_accessories)
                    cabins_list = "" #TODO: easy way to join list?
                    for cabin in list(veh.cabins.keys()):
                        cabins_list += ","+cabin
                        uni_ini[veh_name][cabin] = veh.cabins[cabin]
                    uni_ini[veh_name]["cabins"] = cabins_list[1:]

    with open("output/unifier.ini", "w") as config_file:
        uni_ini.write(config_file)

    shutil.copyfile("library/placeholder files/unifier.py", "output/unifier.py")

def make_vehicle_files(veh, pj, shared_colour = True):
    print("Adding vehicle: "+veh.name)

    make_def_folder(veh)
    make_settings_sui(veh, pj)
    make_vehicle_folder(veh, pj)

    if shared_colour:
        copy_shared_colour_dds(veh, pj)
        make_shared_colour_tobj(veh, pj)

    if veh.separate_paintjobs:
        for cab in veh.cabins:
            cab_size = cab
            cab_name = veh.cabins[cab]
            make_cabin_sii(veh, pj, cab_size, cab_name)
            make_cabin_tobj(pj, veh, cab_size)
            if veh.uses_accessories:
                make_cabin_acc_sii(veh, pj, cab_size)
    else:
        make_only_sii(veh, pj)
        make_only_tobj(pj, veh)
        if veh.uses_accessories:
            make_only_acc_sii(veh, pj)

    if not veh.trailer:
        copy_cabin_dds(pj, veh)

    if veh.uses_accessories:
        make_acc_tobj(veh, pj)
        copy_textured_accessory_dds(veh, pj)

def make_pack(pack):
    clear_output_folder()

    print("")
    print("Making mod: "+pack.name)

    make_manifest_sii(pack)
    copy_mod_manager_image()
    make_material_folder()

    for pj in pack.paintjobs:
        print("")
        print("Making paintjob: "+pj.name)

        copy_paintjob_icon(pj)
        make_paintjob_icon_tobj(pj)
        make_paintjob_icon_mat(pj)

        for veh in pj.vehicles:
            make_vehicle_files(veh, pj)

    make_unifier_ini(pack)

    print("")
    print("Finished")

def save_new_pack_to_database(pack):
    print("Saving new pack to database")

    if os.path.isfile("library/packs/%s/%s.ini" % (pack.game, pack.main_paintjob)):
        print("Pack already exists...")
        oops_input = input("Enter Y to overwrite, N to not overwrite, or anything else to abort: ")

        if oops_input in ("Y", "y"):
            print("Overwriting...")
            shutil.copyfile("new pack.ini", "library/packs/%s/%s.ini" % (pack.game, pack.main_paintjob))
            shutil.copyfile("library/placeholder files/new pack.ini", "new pack.ini")
        elif oops_input in ("N", "n"):
            print("Discarding...")
            shutil.copyfile("library/placeholder files/new pack.ini", "new pack.ini")
        else:
            print("Aborting...")

    else:
        shutil.copyfile("new pack.ini", "library/packs/%s/%s.ini" % (pack.game, pack.main_paintjob))
        shutil.copyfile("library/placeholder files/new pack.ini", "new pack.ini")

def clear_existing_ini():
    shutil.copyfile("library/placeholder files/existing pack.ini", "existing pack.ini")

def save_existing_pack_to_database(pack):
    pack_ini = configparser.ConfigParser()

    pack_ini.add_section("pack info")
    pack_ini["pack info"]["game"] = pack.game
    pack_ini["pack info"]["name"] = pack.name
    pack_ini["pack info"]["version"] = pack.version
    paintjobs = "" #TODO: easy way to join list?
    for pj in pack.list_of_paintjobs:
        paintjobs += ","+pj
    pack_ini["pack info"]["paintjobs"] = paintjobs[1:]
    pack_ini["pack info"]["main paintjob"] = pack.main_paintjob
    relateds = "" #TODO: easy way to join list?
    for rel in pack.list_of_related_packs:
        relateds += ","+rel
    pack_ini["pack info"]["related packs"] = relateds[1:]
    pack_ini["pack info"]["link"] = pack.link
    pack_ini["pack info"]["description"] = pack.brief_desc
    pack_ini["pack info"]["more info"] = pack.more_info

    for pj in pack.paintjobs:
        int_name = pj.int_name[3:]
        pack_ini.add_section(int_name)
        pack_ini[int_name]["name"] = pj.name
        pack_ini[int_name]["price"] = pj.price
        pack_ini[int_name]["main colour"] = pj.colour
        for veh in pj.list_of_vehicles:
            pack_ini[int_name][veh] = "" #TODO: make without delimiter?

    for rel in pack.related_packs:
        pack_ini.add_section(rel.int_name)
        pack_ini[rel.int_name]["description"] = pj.description

    with open("library/packs/%s/%s.ini" % (pack.game, pack.main_paintjob), "w") as config_file:
        pack_ini.write(config_file)

def make_pack_addon(pack, vehicles_to_add):
    for veh in vehicles_to_add:
        for pj in pack.paintjobs:
            pj.list_of_vehicles.append(veh.make+" "+veh.model)
            pj.vehicles.append(veh)

            make_vehicle_files(veh, pj, shared_colour = False)

    make_unifier_ini(pack, vehicles_to_add)
    save_existing_pack_to_database(pack)

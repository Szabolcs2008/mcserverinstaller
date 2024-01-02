import datetime
import getpass
import json
import os
import shutil
import sys
import requests

cmdline_args = sys.argv

print("-----------------------------------------")
print("            MCSERVERINSTALLER            ")
print("-----------------------------------------")
class Logger:
    DEBUG = 0
    INFO = 1
    WARN = 2
    ERR = 3
    FATAL = 4
    SILENT = 5

    def __init__(self):
        super().__init__()
        self.loglevel = self.INFO
        self.logFile = "logs/" + datetime.datetime.now().strftime("%y_%m_%d - %H_%M_%S") + ".log"

        if not os.path.exists("logs/"):
            try:
                os.mkdir("logs/")
                self.log("Successfully created log folder", self.INFO)
            except:
                self.log("Failed to create log folder!", self.FATAL)
                os._exit(1)

    def setLogLevel(self, newLogLevel):
        if newLogLevel <= self.SILENT:
            self.loglevel = newLogLevel
        else:
            raise ValueError("Log level must be between 'DEBUG' and 'SILENT' (0-5)")

    # I don't want to use a proper logger, because it's easier for me like this
    def log(self, message, logLevel=INFO, command=False):
        t = datetime.datetime.now().strftime("%H:%M:%S")
        if command:
            self.__writeToFile(f"[{t}] //{message}")
        else:
            if logLevel != self.SILENT:
                if logLevel == self.INFO:
                    if logLevel >= self.loglevel:
                        print(f"[{t} INFO] {message}")
                    self.__writeToFile(f"[{t} INFO] {message}")
                elif logLevel == self.WARN:
                    if logLevel >= self.loglevel:
                        print(f"\033[33m[{t} WARNING] {message}\033[0m")
                    self.__writeToFile(f"[{t} WARNING] {message}")
                elif logLevel == self.ERR:
                    if logLevel >= self.loglevel:
                        print(f"\033[31m[{t} ERROR] {message}\033[0m")
                    self.__writeToFile(f"[{t} ERROR] {message}")
                elif logLevel == self.FATAL:
                    if logLevel >= self.loglevel:
                        print(f"\033[31;1m[{t} FATAL] {message}\033[0m")
                    self.__writeToFile(f"[{t} FATAL] {message}")
                elif logLevel == self.DEBUG:
                    if logLevel >= self.loglevel:
                        print(f"\033[32m[{t} DEBUG] {message}\033[0m")
                    self.__writeToFile(f"[{t} DEBUG] {message}")
            else:
                raise ValueError("Log level cannot be 'SILENT'!")


    def __writeToFile(self, data, end="\n"):
        with open(self.logFile, "a+") as file:
            file.write(data+end)

logger = Logger()
if "--debug" in cmdline_args:
    logger.setLogLevel(Logger.DEBUG)

def clearConsole():
    cmd = "clear"
    if os.name in ("nt", "dos"):
        cmd = "cls"
    os.system(cmd)

def getDownloadSources():
    url = "https://raw.githubusercontent.com/Szabolcs2008/mcserverinstaller/master/sources.json"
    try:
        resp = requests.get(url)
    except:
        logger.log(
            "Failed to update the download sources! The downloaded files might be out of date! Proceed with caution",
            Logger.WARN)
        return
    if resp.status_code == 200:
        logger.log("Updated file sources", Logger.INFO)
        with open("sources.json", "w+") as sources:
            sources.write(resp.content.decode())
    else:
        if os.path.exists("sources.json"):
            logger.log("Failed to update the download sources! The downloaded files might be out of date! Proceed with caution", Logger.WARN)
        else:
            logger.log("Failed to download the file sources! The program will exit.", Logger.FATAL)


getDownloadSources()

with open("sources.json", "r") as f:
    try:
        sources = json.load(f)
    except Exception as e:
        logger.log(e, Logger.DEBUG)
        logger.log("Failed to load the file download sources. Is the JSON syntax valid?", Logger.FATAL)
        os._exit(1)

def mcVer(id) -> str:
    if id == 0:
        return "vanilla"
    elif id == 1:
        return "spigot"
    elif id == 2:
        return "paper"
    elif id == 3:
        return "purpur"
    elif id == 10:
        return "bungeecord"
    elif id == 11:
        return "waterfall"
    elif id == 12:
        return "velocity"

def download_file(type, name, version, dir=""):
    if sources[type][name][version].split("/")[-1][len(sources[type][name][version].split("/")[-1])-4:] == ".jar":
        filename = sources[type][name][version].split("/")[-1]
    else:
        filename = name+".jar"
    url = sources[type][name][version]
    logger.log(f"Downloading file '{filename}' from '{url}'")
    try:
        response = requests.get(url)
    except:
        logger.log(f"Failed to download file '{filename}'", Logger.ERR)
        return

    if response.status_code == 200:
        with open(dir+filename, 'wb') as file:
            file.write(response.content)
            logger.log(f"Successfully downloaded '{filename}'", Logger.INFO)
    else:
        logger.log(f"Failed to download file '{filename}'. Status code: {response.status_code}", Logger.ERR)

def create(name, template=False):

    server_settings = {
        "software": None,
        "version": None,
        "eula": None,
        "server-port": None,
        "world-name": None,
        "rcon-enabled": None,
        "rcon-port": None,
        "rcon-password": None,
        "online-mode": None,
        "auth_plugin": {"plugins": {},
                        "selected": {"name": None,
                                     "version": None},
                        "download": None},
        "plugins": {"available": {},
                    "ids": {},
                    "plugin_string": None,
                    "plugin_versions": {}}
    }
    idx = 0
    for plugin in sources["plugins"]:
        server_settings["plugins"]["available"][plugin] = list(i for i in sources["plugins"][plugin])
        server_settings["plugins"]["ids"][str(idx)] = plugin
        idx += 1

    for plugin in sources["auth"]:
        server_settings["auth_plugin"]["plugins"][plugin] = list(i for i in sources["auth"][plugin])

    logger.log(json.dumps(server_settings, indent=2), Logger.DEBUG)

    clearConsole()
    print("Available server softwares:")
    print("0 | Vanilla")
    print("1 | Spigot")
    print("* 2 | Paper/Spigot")
    print("3 | Purpur/Spigot")
    # print("10 | Bungeecord")
    # print("11 | Velocity (Bungee)")
    # print("12 | Waterfall (Bungee)")
    while server_settings["software"] == None:
        software = input("Server software [2]: ")
        if software == "":
            software = 2
        try:
            if int(software) > 3:
                print("Software ID must me between 0 and 3")
                server_settings["software"] = None
            else:
                server_settings["software"] = mcVer(int(software))

        except ValueError:
            print("Invalid response")
            server_settings["software"] = None


    print("Select your minecraft version:")
    versions = list(ver for ver in sources["server"][server_settings["software"]])
    for idx in range(len(versions)):
        print(f"{idx} | {versions[idx]}")
    while server_settings["version"] == None:
        version = input("Minecraft version [0]: ")
        if version == "":
            version = 0
        try:
            server_settings["version"] = versions[(int(version))]
            if int(version) > len(versions):
                print(f"Minecraft version should be between 0 and {len(versions)-1}")
                server_settings["version"] = None
        except ValueError:
            print("Invalid number!")
            server_settings["version"] = None

    clearConsole()
    while server_settings["eula"] == None:
        eula = input("Do you accept the Minecraft EULA (y/n) [y]? ")
        if eula.casefold() == "n":
            server_settings["eula"] = False
        elif eula.casefold() == "y":
            server_settings["eula"] = True
        elif eula == "":
            server_settings["eula"] = True
        else:
            print("Invalid response! (y/n)")
            server_settings["eula"] = None

    clearConsole()
    while server_settings["server-port"] == None:
        port = input("Server port [25565]: ")
        if port == "":
            server_settings["server-port"] = 25565
            break
        try:
            server_settings["server-port"] = int(port)
        except ValueError:
            print("Invalid number")
            server_settings["server-port"] = None

    clearConsole()
    while server_settings["world-name"] == None:
        world_name = input("Default world name [world]: ")
        if " " in world_name:
            print("Invalid world name")
            server_settings["world-name"] = None
            continue
        if world_name == "":
            server_settings["world-name"] = "world"
        else:
            server_settings["world-name"] = world_name

    clearConsole()
    while server_settings["rcon-enabled"] == None:
        rcon = input("Rcon enabled (y/n) [n]? ")
        if rcon.casefold() == "n":
            server_settings["rcon-enabled"] = False
        elif rcon.casefold() == "y":
            server_settings["rcon-enabled"] = True
        elif rcon == "":
            server_settings["rcon-enabled"] = False
        else:
            print("Invalid response! (y/n)")
            server_settings["rcon-enabled"] = None

    if server_settings["rcon-enabled"]:
        while server_settings["rcon-port"] == None:
            rcon_port = input("RCON port [25575]: ")
            if rcon_port == "":
                server_settings["rcon-port"] = 25575
                break
            else:
                try:
                    if int(rcon_port) < 65536:
                        server_settings["rcon-port"] = int(rcon_port)
                    else:
                        print("Port number must be between 1 and 65535")
                        server_settings["rcon-port"] = None
                except ValueError:
                    print("Invalid port number")
                    server_settings["rcon-port"] = None

        rcon_password = getpass.getpass(prompt="Rcon password (input hidden) [rconpassword123]: ")
        if rcon_password == "":
            server_settings["rcon-password"] = "rconpassword123"
        else:
            server_settings["rcon-password"] = rcon_password

    clearConsole()
    while server_settings["online-mode"] == None:
        online_mode = input("Online mode (y/n) [y]? ")
        if online_mode.casefold() == "n":
            server_settings["online-mode"] = False
        elif online_mode.casefold() == "y":
            server_settings["online-mode"] = True
        elif online_mode == "":
            server_settings["online-mode"] = True
        else:
            print("Invalid response! (y/n)")
            server_settings["online-mode"] = None

    if not server_settings["online-mode"]:
        print("\033[33;1mWARNING! You're about to create a server in offline mode!\n"
              "This means that anyone can join the server without a minecraft account.\n"
              "It's recommended to install an auth plugin\033[0m")
        while server_settings["auth_plugin"]["download"] == None:
            auth_plugin = input("Do you want to install an auth plugin (y/n) [y]? ")
            if auth_plugin.casefold() == "n":
                server_settings["auth_plugin"]["download"] = False
            elif auth_plugin.casefold() == "y":
                server_settings["auth_plugin"]["download"] = True
            elif auth_plugin == "":
                server_settings["auth_plugin"]["download"] = True
            else:
                print("Invalid response! (y/n)")
                server_settings["auth_plugin"]["download"] = None

    if server_settings["auth_plugin"]["download"]:
        print("Witch auth plugin do you want to use?")
        print("0 | authme (1.7-1.16.x recommended, but works on 1.16+)")
        print("1 | nexauth (1.17+)")
        while server_settings["auth_plugin"]["selected"]["name"] == None:
            auth_plugin_id = input("Choice [0]: ")
            if auth_plugin_id == "":
                server_settings["auth_plugin"]["selected"]["name"] = "authme"
                break
            try:
                if int(auth_plugin_id) == 0:
                    server_settings["auth_plugin"]["selected"]["name"] = "authme"
                elif int(auth_plugin_id) == 1:
                    server_settings["auth_plugin"]["selected"]["name"] = "nexauth"
                else:
                    print("Plugin ID should be 0 or 1")
                    server_settings["auth_plugin"]["selected"]["name"] = None
            except ValueError:
                print("Invalid plugin ID")
                auth_plugin_id = None
        plugin_versions = server_settings["auth_plugin"]["plugins"][server_settings["auth_plugin"]["selected"]["name"]]
        auth_ver = None
        if len(plugin_versions) > 1:
            print("Choose the version for the auth plugin")
            for ver in plugin_versions:
                print(f"{plugin_versions.index(ver)} | {ver}")
            while server_settings["auth_plugin"]["selected"]["version"] == None:
                choice = input("Auth plugin version [0]: ")
                if choice == "":
                    server_settings["auth_plugin"]["selected"]["version"] = plugin_versions[0]
                else:
                    try:
                        server_settings["auth_plugin"]["selected"]["version"] = plugin_versions[int(choice)]
                        if int(choice) > len(plugin_versions):
                            server_settings["auth_plugin"]["selected"]["version"] = None
                            print(f"The version number must be between 0 and {len(plugin_versions)}")
                    except ValueError:
                        print("Invalid number")
                        server_settings["auth_plugin"]["selected"]["version"] = None
                        continue

        else:
            server_settings["auth_plugin"]["selected"]["version"] = "latest"



    clearConsole()
    print("Plugins that can be preinstalled:")
    tmp = 0
    for plugin in server_settings["plugins"]["available"]:
        print(f"{2**tmp} | {plugin}")
        tmp += 1

    print("Type in the sum of the plugin's ids (for example plugin 1 and plugin 3 is 5)")
    while server_settings["plugins"]["plugin_string"] == None:
        plugins = input("Plugins [0]: ")
        if plugins == "":
            server_settings["plugins"]["plugin_string"] = "0"*(len(server_settings["plugins"]["available"])-1)
            break
        try:
            plugins = int(plugins)
        except:
            print("Invalid number.")
            server_settings["plugins"]["plugin_string"] = None
            continue
        plugins = ("{:0"+str(len(server_settings["plugins"]["available"]))+"b}").format(int(plugins))
        if len(plugins) > len(sources["plugins"]):
            print("Too large plugin int. Please check your calculations")
            server_settings["plugins"]["plugin_string"] = None
        else:
            server_settings["plugins"]["plugin_string"] = plugins[::-1]

    for idx in range(len(server_settings["plugins"]["available"])):
        if server_settings["plugins"]["plugin_string"][idx] == "1":
            if len(server_settings["plugins"]["available"][server_settings["plugins"]["ids"][str(idx)]]) > 1:

                print("Choose version for plugin '"+server_settings["plugins"]["ids"][str(idx)]+"'")
                tmp = 0
                for ver in sources["plugins"][server_settings["plugins"]["ids"][str(idx)]]:
                    print(f"{tmp} | {ver}")
                    tmp += 1
                server_settings["plugins"]["plugin_versions"][server_settings["plugins"]["ids"][str(idx)]] = None
                while server_settings["plugins"]["plugin_versions"][server_settings["plugins"]["ids"][str(idx)]] == None:
                    choice = input("Plugin version [0]: ")
                    if choice == "":
                        server_settings["plugins"]["plugin_versions"][server_settings["plugins"]["ids"][str(idx)]] = server_settings["plugins"]["available"][server_settings["plugins"]["ids"][str(idx)]][0]
                        break
                    try:
                        if not int(choice) <= tmp:
                            print(f"The answer must be between 0 and {tmp}")
                            server_settings["plugins"]["plugin_versions"][server_settings["plugins"]["ids"][str(idx)]] = None
                        server_settings["plugins"]["plugin_versions"][server_settings["plugins"]["ids"][str(idx)]] = server_settings["plugins"]["available"][server_settings["plugins"]["ids"][str(idx)]][int(choice)]
                    except:
                        print("Invalid number")
                        server_settings["plugins"]["plugin_versions"][server_settings["plugins"]["ids"][str(idx)]] = None
                        continue


            else:
                server_settings["plugins"]["plugin_versions"][server_settings["plugins"]["ids"][str(idx)]] = "latest"


    if not template:
        if server_settings["software"] in ("vanilla", "spigot", "paper", "purpur"):
            logger.log("Creating directories...", Logger.INFO)
            try:
                os.makedirs(name)
                os.makedirs(name+"/"+world_name+"/datapacks")
                os.makedirs(name+"/plugins")
            except Exception as e:
                logger.log("Failed to create a server directory. ", Logger.FATAL)
                logger.log(f"Exception: {e}", Logger.FATAL)
                return
            logger.log("Creating server.properties", Logger.INFO)

            # user inputted settings
            with open(name+"/server.properties", 'w') as server_properties:
                if server_settings["rcon-password"] == None:
                    server_settings["rcon-password"] = ""
                data = [f"server-port="+str(server_settings["server-port"]),
                        f"enable-rcon="+str(server_settings["rcon-enabled"]).casefold(),
                        f"rcon.password="+server_settings["rcon-password"],
                        f"rcon.port="+str(server_settings["rcon-port"]),
                        f"level-name="+server_settings["world-name"],
                        f"online-mode="+str(server_settings["online-mode"]).casefold()]
                server_properties.write("\n".join(data))
            if server_settings["eula"]:
                with open(name+"/eula.txt", 'w') as eula_file:
                    eula_file.write("eula=true")
            else:
                with open(name+"/eula.txt", 'w') as eula_file:
                    eula_file.write("eula=false")


            logger.log(server_settings["plugins"]["plugin_string"], Logger.DEBUG)
            # download jars
            logger.log("Downloading jars...", Logger.INFO)
            download_file(type="server", name=server_settings["software"], version=server_settings["version"],
                          dir=name+"/")
            for plugin in server_settings["plugins"]["plugin_versions"]:
                download_file(type="plugins", name=plugin, version=server_settings["plugins"]["plugin_versions"][plugin], dir=name+"/plugins/")
            logger.log("Your server is ready.")


# if not os.path.exists("templates/"):
#     os.mkdir("templates/")
try:
    while True:
        cmd = input("> ").split(" ")
        logger.log(" ".join(cmd), command=True)
        if cmd[0].casefold() == "exit":
            logger.log("Exiting...", Logger.INFO)
            break
        elif cmd[0].casefold() == "help":
            logger.log("-----------------------------------------", Logger.INFO)
            logger.log("                   HELP                  ", Logger.INFO)
            logger.log("-----------------------------------------", Logger.INFO)
            logger.log("exit | Exits the program", Logger.INFO)
            logger.log("new <name> [template (not finished)]| Creates a new server", Logger.INFO)
            logger.log("delete <name> | deletes a server", Logger.INFO)
            # TODO: actually implement templates
            # logger.log("template <...>", Logger.INFO)
            # logger.log("          create <name> | Creates a new server template", Logger.INFO)
            # logger.log("          delete <name> | Creates a new server template", Logger.INFO)
            # logger.log("          display <name> | Prints the data of a template", Logger.INFO)
            # logger.log("          list | Lists the available templates", Logger.INFO)
        elif cmd[0].casefold() == "new":
            if len(cmd) >= 2:
                create(cmd[1])
            else:
                logger.log("Usage: new <name> [template]", Logger.ERR)
        elif cmd[0].casefold() == "delete":
            if len(cmd) == 2:
                if cmd[1].casefold() in ("logs", "templates", "/", "C:/"):
                    logger.log("You can not delete this folder.", Logger.ERR)
                logger.log(f"YOU ARE ABOUT TO DELETE '{cmd[1]}' ARE YOU SURE?", Logger.WARN)
                choice = None
                while choice == None:
                    choice = input("do you want to continue (y/n) [n]? ")
                    if choice == "":
                        choice = "n"
                    elif choice.casefold() == "y":
                        logger.log(f"Deleting server '{cmd[1]}'")
                        shutil.rmtree(cmd[1])
                    elif choice.casefold() == "n":
                        logger.log("Cancelled.")
            else:
                logger.log("Usage: delete <name>", Logger.ERR)
except KeyboardInterrupt:
    logger.log("Exiting...", Logger.INFO)
    os._exit(0)

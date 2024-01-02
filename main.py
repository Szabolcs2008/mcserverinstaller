import datetime
import getpass
import json
import os
import shutil
import sys
import requests

cmdline_args = sys.argv


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
logger.setLogLevel(Logger.DEBUG)

def cleatConsole():
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

    server_software = None
    minecraft_version = None
    eula = None
    port = None
    world_name = None
    rcon = None
    rcon_password = None
    online_mode = None

    auth_plugin = None
    auth_plugin_id = None

    plugins = None

    cleatConsole()
    print("Available server softwares:")
    print("0 | Vanilla")
    print("1 | Spigot")
    print("* 2 | Paper/Spigot")
    print("3 | Purpur/Spigot")
    print("10 | Bungeecord")
    print("11 | Velocity (Bungee)")
    print("12 | Waterfall (Bungee)")
    while server_software == None:
        server_software = input("Server software [2]: ")
        if server_software == "":
            server_software = 2
            break
        try:
            server_software = int(server_software)
        except ValueError:
            print("Invalid response")

    print("Select your minecraft version:")
    tmp = 0
    versions = []
    for ver in sources["server"][mcVer(server_software)]:
        print(f"{tmp} | {ver}")
        tmp += 1
        versions.append(ver)
    while minecraft_version == None:
        minecraft_version = input("Minecraft version [0]: ")
        if minecraft_version == "":
            minecraft_version = 0
            break
        try:
            minecraft_version = int(minecraft_version)
            if minecraft_version > tmp:
                print(f"Minecraft version should be between 0 and {tmp-1}")
                minecraft_version = None
        except ValueError:
            print("Invalid number!")
            minecraft_version = None

    cleatConsole()
    while eula == None:
        eula = input("Do you accept the Minecraft EULA (y/n) [y]? ")
        if eula.casefold() == "n":
            eula = False
        elif eula.casefold() == "y":
            eula = True
        elif eula == "":
            eula = True
        else:
            print("Invalid response! (y/n)")
            eula = None

    cleatConsole()
    while port == None:
        port = input("Server port [25565]: ")
        if port == "":
            port = 25565
            break
        try:
            port = int(port)
        except ValueError:
            port = None

    cleatConsole()
    world_name = input("Default world name [world]: ")
    if world_name == "":
        world_name = "world"

    cleatConsole()
    while rcon == None:
        rcon = input("Rcon enabled (y/n) [n]? ")
        if rcon.casefold() == "n":
            rcon = False
        elif rcon.casefold() == "y":
            rcon = True
        elif rcon == "":
            rcon = False
        else:
            print("Invalid response! (y/n)")
            rcon = None

    if rcon:
        rcon_password = getpass.getpass(prompt="Rcon password: (rconpassword123) ")
        if rcon_password == "":
            rcon_password = "rconpassword123"

    cleatConsole()
    while online_mode == None:
        online_mode = input("Online mode (y/n) [y]? ")
        if online_mode.casefold() == "n":
            online_mode = False
        elif online_mode.casefold() == "y":
            online_mode = True
        elif online_mode == "":
            online_mode = True
        else:
            print("Invalid response! (y/n)")
            online_mode = None

    if not online_mode:
        print("\033[33;1mWARNING! You're about to create a server in offline mode!\n"
              "This means that anyone can join the server without a minecraft account.\n"
              "It's recommended to install an auth plugin\033[0m")
        while auth_plugin == None:
            auth_plugin = input("Do you want to install an auth plugin (y/n) [y]? ")
            if auth_plugin.casefold() == "n":
                auth_plugin = False
            elif auth_plugin.casefold() == "y":
                auth_plugin = True
            elif auth_plugin == "":
                auth_plugin = True
            else:
                print("Invalid response! (y/n)")
                auth_plugin = None

    if auth_plugin:
        print("Witch auth plugin do you want to use?")
        print("0 | authme (1.7-1.16.x recommended, but works on 1.16+)")
        print("1 | nexauth (1.17+)")
        while auth_plugin_id == None:
            auth_plugin_id = input("Choice [0]: ")
            if auth_plugin_id == "":
                auth_plugin_id = 0
                break
            try:
                auth_plugin_id = int(auth_plugin_id)
                if auth_plugin_id > 1:
                    print("Plugin ID should be 0 or 1")
                    auth_plugin_id = None
            except:
                print("Invalid plugin ID")
                auth_plugin_id = None
        auth_plugins = list(name for name in sources["auth"])
        plugin_versions = list(ver for ver in sources["auth"][auth_plugins[auth_plugin_id]])
        auth_ver = None
        if len(plugin_versions) > 1:
            print("Choose the version for the auth plugin")
            for ver in plugin_versions:
                print(f"{plugin_versions.index(ver)} | {ver}")
            while auth_ver == None:
                choice = input("Auth plugin version [0]: ")
                if choice == "":
                    auth_ver = 0
                else:
                    try:
                        choice = int(choice)
                    except:
                        print("Invalid number")
                        auth_ver = None
                        continue
                    if choice > len(plugin_versions):
                        auth_ver = None
                        print(f"The version number must be between 0 and {len(plugin_versions)}")
        else:
            auth_ver = "latest"



    cleatConsole()
    print("Plugins that can be preinstalled:")
    tmp = 0
    plugin_list = []
    for plugin in sources["plugins"]:
        print(f"{2**tmp} | {plugin}")
        tmp += 1
        plugin_list.append([plugin, None])

    print("Type in the sum of the plugin's ids (for example plugin 1 and plugin 3 is plugin int 5)")
    while plugins == None:
        plugins = input("Plugins [0]: ")
        if plugins == "":
            plugins = 0
            break
        try:
            plugins = int(plugins)
        except:
            print("Invalid number.")
            plugins = None
            continue
        plugins = ("{:0"+str(len(sources["plugins"]))+"b}").format(int(plugins))
        if len(plugins) > len(sources["plugins"]):
            print("Too large plugin int. Please check your calculations")
            plugins = None

    for plugin in plugin_list:
        if len(sources["plugins"][plugin[0]]) > 1:
            versions = []
            for ver in sources["plugins"][plugin[0]]:
                versions.append(ver)

            print(f"Choose version for plugin '{plugin[0]}'")
            tmp = 0
            for ver in sources["plugins"][plugin[0]]:
                print(f"{tmp} | {ver}")
                tmp += 1
            while plugin_list[plugin_list.index(plugin)][1] == None:
                choice = input("Plugin version [0]: ")
                if choice == "":
                    plugin_list[plugin_list.index(plugin)][1] = 0
                    break
                try:
                    choice = int(choice)
                except:
                    print("Invalid number")
                    plugin_list[plugin_list.index(plugin)][1] = None
                if not choice <= tmp:
                    print(f"The answer must be between 0 and {tmp}")
                    plugin_list[plugin_list.index(plugin)][1] = None

        else:
            plugin_list[plugin_list.index(plugin)][1] = "latest"



    if not template:
        if server_software <= 3:  # 0-3 are the spigot/bukkit forks
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
            with open(name+"/server.properties", 'w') as server_properties:
                if rcon_password == None:
                    rcon_password = ""
                data = [f"server-port={port}",
                        f"enable-rcon={str(rcon).casefold()}",
                        f"rcon.password={rcon_password}",
                        f"level-name={world_name}",
                        f"online-mode={str(online_mode).casefold()}"]
                server_properties.write("\n".join(data))
            logger.log("Downloading jars...", Logger.INFO)
            download_file(type="server", name=mcVer(server_software), version=versions[minecraft_version], dir=name+"/")
            plugin_str = plugins
            logger.log(f"plugin_str = {plugin_str}", Logger.DEBUG)
            plugin_list.reverse()
            for idx in range(len(plugin_str)):
                plugin = plugin_list[idx][0]
                version = plugin_list[idx][1]
                download = plugin_str[idx]
                logger.log(f"plugin: {plugin}, {version}, {download}", Logger.DEBUG)
                if download == "1":
                    download_file(type="plugins", name=plugin, version=version, dir=f"{name}/plugins/")
            if auth_plugin:
                if auth_plugin_id == 0:
                    plugin = "authme"
                    download_file(type="auth", name=plugin, version=auth_ver, dir=f"{name}/plugins/")
                else:
                    plugin = "nexauth"
                    download_file(type="auth", name=plugin, version=auth_ver, dir=f"{name}/plugins/")

                logger.log(f"Auth plugin: {plugin}, {auth_ver}", Logger.DEBUG)
            logger.log("Done.")
            logger.log(f"You can start your server with the command 'java -Xmx4G -jar <server jar> --nogui' or by double clicking the server jar.")



        else:
            logger.log("Editing bungee settings is not supported yet. The files will be downloaded, but the settings will not be saved.", Logger.WARN)


if not os.path.exists("templates/"):
    os.mkdir("templates/")
try:
    while True:
        cmd = input("> ").split(" ")
        logger.log(" ".join(cmd), command=True)
        if cmd[0].casefold() == "exit":
            logger.log("Exiting...", Logger.INFO)
            break
        elif cmd[0].casefold() == "help":
            logger.log("-----------------------------------------", Logger.INFO)
            logger.log("            MCSERVERINSTALLER            ", Logger.INFO)
            logger.log("-----------------------------------------", Logger.INFO)
            logger.log("exit | Exits the program", Logger.INFO)
            logger.log("new <name> [template (not finished)]| Creates a new server", Logger.INFO)
            logger.log("delete <name> | deletes a server", Logger.INFO)
            #logger.log("installdir <path> | sets the installation directory", Logger.INFO)
            #logger.log("template <...>", Logger.INFO)
            #logger.log("          create <name> | Creates a new server template", Logger.INFO)
            #logger.log("          delete <name> | Creates a new server template", Logger.INFO)
            #logger.log("          display <name> | Prints the data of a template", Logger.INFO)
            #logger.log("          list | Lists the available templates", Logger.INFO)
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

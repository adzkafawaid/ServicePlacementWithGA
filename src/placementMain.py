from GAworker import run_GA
import json

class EnvConfig:
    def __init__(self, app_json_path, net_json_path, users_json_path):
        with open(app_json_path, "r") as f:
            self.app_json = json.load(f)
        with open(net_json_path, "r") as f:
            self.net_json = json.load(f)
        with open(users_json_path, "r") as f:
            self.users_json = json.load(f)
        self.numberOfNodes = len(self.net_json["entity"])
        self.numberOfServices = sum(len(app["module"]) for app in self.app_json)
        self.module2idx = {}
        self.idx2module = {}
        idx = 0
        for app in self.app_json:
            app_name = app["name"]
            for module in app["module"]:
                mod_name = module["name"]
                self.module2idx[(app_name, mod_name)] = idx
                self.idx2module[idx] = (app_name, mod_name)
                idx += 1
        self.nodeResources = [entity.get("RAM", 10) for entity in self.net_json["entity"]]
        self.serviceResources = []
        for app in self.app_json:
            for module in app["module"]:
                self.serviceResources.append(module.get("RAM", 1))
        self.objectivesFunctions = [["meanResourceUsage", "self.meanResourceUsage()"]]
        self.Gdistances = {}
        self.clientNodes = []

        # --- Mapping kebutuhan user: (app, module_tujuan, node_user) ---
        self.user_module_node = set()
        for user in self.users_json["sources"]:
            app = str(user["app"])
            node = user["id_resource"]
            msg = user["message"]
            app_obj = next((a for a in self.app_json if a["name"] == app), None)
            if app_obj:
                msg_obj = next((m for m in app_obj["message"] if m["name"] == msg), None)
                if msg_obj:
                    mod_dst = msg_obj["d"]
                    self.user_module_node.add((app, mod_dst, node))

    def getNumberOfNodes(self):
        return self.numberOfNodes

    def getNumberOfServices(self):
        return self.numberOfServices

    def getObjectivesFunctions(self):
        return self.objectivesFunctions

    def getNodeResources(self):
        return self.nodeResources

    def getServiceResources(self):
        return self.serviceResources

class GAConfig:
    numberOfSolutionsInWorkers = 10
    numberOfGenerations = 5
    mutationProbability = 0.2
    randomSeed4Optimization = [42]

ec = EnvConfig("data/appDefinition.json", "data/networkDefinition.json", "data/usersDefinition.json")
cnf_ = GAConfig()

if __name__ == "__main__":
    best_sol = run_GA(ec, cnf_)
    chromosome = best_sol.getChromosome()

    print("\n=== DEBUG: Mapping Kromosom Solusi Terbaik ===")
    for idx, allocation in enumerate(chromosome):
        app_name, mod_name = ec.idx2module[idx]
        print(f"Service ke-{idx} (App: {app_name}, Module: {mod_name}): {allocation}")
    print("Jumlah node:", ec.getNumberOfNodes())
    print("Jumlah service:", ec.getNumberOfServices())
    print("Kapasitas RAM tiap node:", ec.getNodeResources())
    print("Total RAM semua node:", sum(ec.getNodeResources()))
    print("Kapasitas RAM tiap service:", ec.getServiceResources())

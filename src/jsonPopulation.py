from yafs.population import Population
from yafs.distribution import exponentialDistribution


class JSONPopulation(Population):
    def __init__(self, json, iteration,**kwargs):
        super(JSONPopulation, self).__init__(**kwargs)
        self.data = json
        self.it = iteration


    def initial_allocation(self, sim, app_name):
            # Deploy sources berdasarkan data user
            for item in self.data["sources"]:
                if item["app"] == app_name:
                    app_name = item["app"]
                    idtopo = item["id_resource"]
                    lambd = item["lambda"]

                    app = sim.apps[app_name]
                    msg = app.get_message(item["message"])
                    
                    # Debug info
                    print(f"[JSONPopulation] App {app_name}: found message {item['message']}: {msg}")
                    print(f"[JSONPopulation] Message source: {msg.src}, dest: {msg.dst}")

                    seed = item["id_resource"]*1000+item["lambda"]+self.it
                    dDistribution = exponentialDistribution(name="Exp", lambd=lambd, seed=seed)

                    # Deploy source - pastikan menggunakan modul "None"
                    idsrc = sim.deploy_source(app_name, id_node=idtopo, msg=msg, distribution=dDistribution)
                    print(f"[JSONPopulation] Deployed source {idsrc} for app {app_name} at node {idtopo}")
                    
                    # Pastikan source terhubung dengan benar dan tampilkan
                    if idsrc is not None:
                        print(f"[JSONPopulation] Source {idsrc} successfully deployed with module: None")
                    else:
                        print(f"[JSONPopulation] ERROR: Failed to deploy source for app {app_name}")




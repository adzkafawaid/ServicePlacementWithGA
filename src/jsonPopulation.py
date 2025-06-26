from yafs.population import Population
from yafs.distribution import exponentialDistribution


class JSONPopulation(Population):
    def __init__(self, json, iteration,**kwargs):
        super(JSONPopulation, self).__init__(**kwargs)
        self.data = json
        self.it = iteration


    def initial_allocation(self, sim, app_name):
            print(f"[JSONPopulation] Starting deployment for app {app_name}")
            
            # Deploy sources berdasarkan data user
            for item in self.data["sources"]:
                if item["app"] == app_name:
                    idtopo = item["id_resource"]
                    lambd = item["lambda"]
                    message_name = item["message"]

                    print(f"[JSONPopulation] Processing user for app {app_name} at node {idtopo}")
                    
                    app = sim.apps[app_name]
                    msg = app.get_message(message_name)
                    
                    if msg is None:
                        print(f"[JSONPopulation] ERROR: Message {message_name} not found in app {app_name}")
                        continue
                    
                    print(f"[JSONPopulation] Found message {message_name}: src={msg.src}, dst={msg.dst}")

                    seed = item["id_resource"]*1000+item["lambda"]+self.it
                    dDistribution = exponentialDistribution(name="Exp", lambd=lambd, seed=seed)

                    # Deploy source dengan message yang tepat
                    print(f"[JSONPopulation] Deploying source for app {app_name} at node {idtopo} with message {message_name}")
                    idsrc = sim.deploy_source(app_name, id_node=idtopo, msg=msg, distribution=dDistribution)
                    
                    if idsrc is not None:
                        print(f"[JSONPopulation] ✅ Source {idsrc} deployed successfully at node {idtopo}")
                    else:
                        print(f"[JSONPopulation] ❌ Failed to deploy source at node {idtopo}")
            
            print(f"[JSONPopulation] Deployment completed for app {app_name}")




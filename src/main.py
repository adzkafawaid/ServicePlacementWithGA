import os
import time
import json
import networkx as nx
import logging.config
import random
import numpy as np

from yafs.core import Sim
from yafs.application import Application, Message
from yafs.topology import Topology
from yafs.distribution import exponentialDistribution
from yafs.application import fractional_selectivity
from yafs.placement import JSONPlacement
from jsonPopulation import JSONPopulation

def create_applications_from_json(data):
    applications = {}
    for app in data:
        a = Application(name=app["name"])
        # Set modules termasuk source module "None"
        modules = [{"None": {"Type": Application.TYPE_SOURCE}}]
        for module in app["module"]:
            modules.append({module["name"]: {"RAM": module["RAM"], "Type": Application.TYPE_MODULE}})
        a.set_modules(modules)

        ms = {}
        # Buat semua messages terlebih dahulu
        for message in app["message"]:
            ms[message["name"]] = Message(
                message["name"], message["s"], message["d"],
                instructions=message["instructions"], bytes=message["bytes"]
            )
        
        # Add source messages (messages yang berasal dari "None")
        for message in app["message"]:
            if message["s"] == "None":
                a.add_source_messages(ms[message["name"]])
                print(f"[DEBUG] Added source message {message['name']} for app {app['name']}")

        # Add service modules dan transmissions
        for trans in app["transmission"]:
            if "message_out" in trans:
                a.add_service_module(trans["module"], ms[trans["message_in"]], ms[trans["message_out"]], fractional_selectivity, threshold=1.0)
            else:
                a.add_service_module(trans["module"], ms[trans["message_in"]])

        applications[app["name"]] = a
    return applications

def main(simulated_time, path, pathResults, it):
    # Load topology
    t = Topology()
    dataNetwork = json.load(open(os.path.join(path, 'networkDefinition.json')))
    t.load(dataNetwork)
    nx.write_gexf(t.G, os.path.join(path, "network.gexf"))

    # Load applications
    dataApp = json.load(open(os.path.join(path, 'appDefinition.json')))
    apps = create_applications_from_json(dataApp)

    # Load placement (pakai hasil GA)
    placementJson = json.load(open(os.path.join(path, 'allocDefinitionGA.json')))
    placement = JSONPlacement(name="Placement", json=placementJson)

    # Load population
    dataPopulation = json.load(open(os.path.join(path, 'usersDefinition.json')))

    # DEBUG: Print info
    print("=== DEBUG INFO ===")
    print(f"Total nodes in topology: {len(t.G.nodes())}")
    print(f"Total edges in topology: {len(t.G.edges())}")
    print(f"Apps created: {list(apps.keys())}")
    print(f"Total allocation entries: {len(placementJson['initialAllocation'])}")
    print(f"Total user sources: {len(dataPopulation['sources'])}")
    
    # SIMULATION ENGINE
    stop_time = simulated_time
    s = Sim(t, default_results_path=os.path.join(pathResults, f"Results_{stop_time}_{it}"))

    # Deploy per aplikasi
    for aName in apps.keys():
        print(f"\n=== Processing App: {aName} ===")
        data = [element for element in dataPopulation["sources"] if str(element.get('app', '')) == aName]
        print(f"Found {len(data)} users for app {aName}")
        
        if data:
            print(f"User data: {data}")
            # Lambda diambil dari JSON jika ada, jika tidak random
            lambd = data[0]["lambda"] if data and "lambda" in data[0] else random.randint(100, 1000)
            distribution = exponentialDistribution(name="Exp", lambd=lambd, seed=int(aName)*100+it)
            pop_app = JSONPopulation({"sources": data}, it, name=f"Pop_{aName}")
            print(f"Deploying app {aName} with placement...")
            s.deploy_app(apps[aName], placement, pop_app)
            print(f"App {aName} deployed successfully")
        else:
            print(f"No users found for app {aName}")

    print(f"\nRunning simulation for {stop_time} units...")
    s.run(stop_time, test_initial_deploy=False, show_progress_monitor=False)
    print("Simulation finished.")

if __name__ == '__main__':
    # Path setup
    runpath = os.getcwd()
    pathExperimento = "data/"  # Ganti sesuai lokasi file JSON kamu
    nSimulations = 1
    timeSimulation = 10000
    datestamp = time.strftime('%Y%m%d')
    dname = os.path.join(pathExperimento, f"results_{datestamp}/")
    os.makedirs(dname, exist_ok=True)

    for i in range(nSimulations):
        start_time = time.time()
        random.seed(i)
        np.random.seed(i)
        main(simulated_time=timeSimulation, path=pathExperimento, pathResults=dname, it=i)
        print(f"\n--- {time.time() - start_time:.2f} seconds ---")

    print("Simulation Done")
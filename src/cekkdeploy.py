import sys, os
sys.path.append(os.getcwd())
from main import *
import json

# Load data
t = Topology()
dataNetwork = json.load(open('src/data/networkDefinition.json'))
t.load(dataNetwork)

dataApp = json.load(open('src/data/appDefinition.json'))
apps = create_applications_from_json(dataApp[:1])  # Test dengan 1 app saja

placementJson = json.load(open('src/data/allocDefinitionGA.json'))
placement = JSONPlacement(name='Placement', json=placementJson)

dataPopulation = json.load(open('src/data/usersDefinition.json'))

# Test dengan app 0 saja
from yafs.core import Sim
s = Sim(t)
app_name = '0'
data = [element for element in dataPopulation['sources'] if str(element.get('app', '')) == app_name]
print(f"Found {len(data)} users for app {app_name}: {data}")

if data:
    pop_app = JSONPopulation({'sources': data}, 0, name=f'Pop_{app_name}')
    print('Deploying app 0...')
    
    # Deploy app dengan 3 parameter yang diperlukan
    print("Deploying app with placement and population...")
    s.deploy_app(apps[app_name], placement, pop_app)
    
    print('Done')
    
    # Cek hasil deployment
    print(f"Apps in simulator: {list(s.apps.keys())}")
    if app_name in s.apps:
        app = s.apps[app_name]
        print(f"App {app_name} has {len(app.messages)} messages")
        for msg in app.messages:
            print(f"  Message: {msg}")
    
    # Manual run untuk melihat apakah source bekerja
    print("Testing short simulation run...")
    try:
        s.run(10)  # Run 10 time units
        print("Simulation completed successfully")
    except Exception as e:
        print(f"Simulation error: {e}")
    
    print("Debug completed")
    
else:
    print("No data found for app 0")
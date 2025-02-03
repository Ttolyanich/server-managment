from flask import Flask, render_template, request, redirect, jsonify
import json
import os

app = Flask(__name__)
DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"servers": []}
    with open(DATA_FILE, "r") as file:
        return json.load(file)

def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

@app.route('/')
def index():
    data = load_data()
    servers_with_resources = []
    
    for server in data["servers"]:
        if server.get("deleted", False):
            continue

        virtual_machines = server.get("virtual_machines", [])
        used_cpu = sum(vm['cpu'] for vm in virtual_machines)
        used_ram = sum(vm['ram'] for vm in virtual_machines)
        used_ssd = sum(vm['ssd'] for vm in virtual_machines)
        used_hdd = sum(vm['hdd'] for vm in virtual_machines)

        free_cpu = server['cpu'] - used_cpu
        free_ram = server['ram'] - used_ram
        free_ssd = server['ssd'] - used_ssd
        free_hdd = server['hdd'] - used_hdd

        servers_with_resources.append({
            'server': server,
            'used_resources': {
                'used_cpu': used_cpu,
                'used_ram': used_ram,
                'used_ssd': used_ssd,
                'used_hdd': used_hdd
            },
            'free_resources': {
                'free_cpu': free_cpu,
                'free_ram': free_ram,
                'free_ssd': free_ssd,
                'free_hdd': free_hdd
            }
        })

    return render_template('index.html', servers=servers_with_resources)

@app.route('/view_server/<int:server_id>')
def view_server(server_id):
    data = load_data()
    for server in data["servers"]:
        if server["id"] == server_id and not server.get("deleted", False):
            virtual_machines = server.get("virtual_machines", [])
            used_cpu = sum(vm['cpu'] for vm in virtual_machines)
            used_ram = sum(vm['ram'] for vm in virtual_machines)
            used_ssd = sum(vm['ssd'] for vm in virtual_machines)
            used_hdd = sum(vm['hdd'] for vm in virtual_machines)

            free_cpu = server['cpu'] - used_cpu
            free_ram = server['ram'] - used_ram
            free_ssd = server['ssd'] - used_ssd
            free_hdd = server['hdd'] - used_hdd

            return render_template('view_server.html', server=server, virtual_machines=virtual_machines, 
                                   used_resources={'used_cpu': used_cpu, 'used_ram': used_ram, 
                                                   'used_ssd': used_ssd, 'used_hdd': used_hdd},
                                   free_cpu=free_cpu, free_ram=free_ram, free_ssd=free_ssd, free_hdd=free_hdd)
    return "Server not found", 404

@app.route('/edit_vm/<int:vm_id>', methods=['GET', 'POST'])
def edit_vm(vm_id):
    data = load_data()
    for server in data["servers"]:
        for vm in server.get("virtual_machines", []):
            if vm["id"] == vm_id:
                if request.method == 'POST':
                    vm["name"] = request.form['name']
                    vm["cpu"] = int(request.form['cpu'])
                    vm["ram"] = int(request.form['ram'])
                    vm["ssd"] = int(request.form['ssd'])
                    vm["hdd"] = int(request.form['hdd'])
                    save_data(data)
                    return redirect(f'/edit_server/{server["id"]}')
                return render_template('edit_vm.html', vm=vm, server_id=server["id"])
    return "VM not found", 404

@app.route('/edit_server/<int:server_id>', methods=['GET', 'POST'])
def edit_server(server_id):
    data = load_data()
    for server in data["servers"]:
        if server["id"] == server_id:
            if request.method == 'POST':
                server["name"] = request.form['name']
                server["cpu"] = int(request.form['cpu'])
                server["ram"] = int(request.form['ram'])
                server["ssd"] = int(request.form['ssd'])
                server["hdd"] = int(request.form['hdd'])
                save_data(data)
                return redirect('/admin')
            return render_template('server_details.html', server=server, virtual_machines=server.get("virtual_machines", []))
    return "Server not found", 404

@app.route('/add_vm/<int:server_id>', methods=['POST'])
def add_vm(server_id):
    data = load_data()
    for server in data["servers"]:
        if server["id"] == server_id:
            new_vm = {
                "id": len(server.get("virtual_machines", [])) + 1,
                "name": request.form['name'],
                "cpu": int(request.form['cpu']),
                "ram": int(request.form['ram']),
                "ssd": int(request.form['ssd']),
                "hdd": int(request.form['hdd']),
                "deleted": False,
                "server_id": server_id
            }
            server.setdefault("virtual_machines", []).append(new_vm)
            save_data(data)
            return redirect(f'/edit_server/{server_id}')
    return "Server not found", 404

@app.route('/admin')
def admin():
    data = load_data()
    return render_template('admin.html', servers=data["servers"])

if __name__ == '__main__':
    app.run()

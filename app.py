from flask import Flask, render_template, request, redirect
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

# Возвращает следующий уникальный id для сервера
def get_next_server_id(data):
    if data["servers"]:
        return max(server["id"] for server in data["servers"]) + 1
    return 1

# Возвращает следующий уникальный id для виртуальной машины (сканируем все серверы)
def get_next_vm_id(data):
    max_id = 0
    for server in data["servers"]:
        for vm in server.get("virtual_machines", []):
            if vm["id"] > max_id:
                max_id = vm["id"]
    return max_id + 1

# -------------------- Основные маршруты --------------------

# Главная страница - список серверов (без удалённых)
@app.route('/')
def index():
    data = load_data()
    # Выбираем только серверы, не помеченные как удалённые
    servers = [server for server in data["servers"] if not server.get("deleted", False)]
    servers_with_resources = []

    for server in servers:
        # Для расчёта ресурсов выбираем ВМ, у которых deleted == False
        vms = [vm for vm in server.get("virtual_machines", []) if not vm.get("deleted", False)]
        used_cpu = sum(vm['cpu'] for vm in vms)
        used_ram = sum(vm['ram'] for vm in vms)
        used_ssd = sum(vm['ssd'] for vm in vms)
        used_hdd = sum(vm['hdd'] for vm in vms)

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

# Страница администрирования серверов (показываем все серверы)
@app.route('/admin')
def admin():
    data = load_data()
    return render_template('admin.html', servers=data["servers"])

# -------------------- Серверы --------------------

# Маршрут для добавления нового сервера
@app.route('/add_server', methods=['POST'])
def add_server():
    data = load_data()
    new_server = {
        "id": get_next_server_id(data),
        "name": request.form['name'],
        "cpu": int(request.form['cpu']),
        "ram": int(request.form['ram']),
        "ssd": int(request.form['ssd']),
        "hdd": int(request.form['hdd']),
        "deleted": False,
        "virtual_machines": []
    }
    data["servers"].append(new_server)
    save_data(data)
    return redirect('/admin')

# Маршрут для редактирования сервера (GET и POST)
@app.route('/edit_server/<int:server_id>', methods=['GET', 'POST'])
def edit_server(server_id):
    data = load_data()
    server = next((s for s in data["servers"] if s["id"] == server_id), None)
    if not server:
        return "Server not found", 404

    if request.method == 'POST':
        server["name"] = request.form['name']
        server["cpu"] = int(request.form['cpu'])
        server["ram"] = int(request.form['ram'])
        server["ssd"] = int(request.form['ssd'])
        server["hdd"] = int(request.form['hdd'])
        save_data(data)
        return redirect('/admin')
    else:
        # Показываем только виртуальные машины, у которых deleted == False
        vms = [vm for vm in server.get("virtual_machines", []) if not vm.get("deleted", False)]
        return render_template('server_details.html', server=server, virtual_machines=vms)

# Маршрут для пометки сервера как удалённого (soft-delete)
@app.route('/delete_server/<int:server_id>')
def delete_server(server_id):
    data = load_data()
    server = next((s for s in data["servers"] if s["id"] == server_id), None)
    if not server:
        return "Server not found", 404
    server["deleted"] = True
    save_data(data)
    return redirect('/admin')

# Маршрут для восстановления сервера
@app.route('/restore_server/<int:server_id>')
def restore_server(server_id):
    data = load_data()
    server = next((s for s in data["servers"] if s["id"] == server_id), None)
    if not server:
        return "Server not found", 404
    server["deleted"] = False
    save_data(data)
    return redirect('/admin')

# Маршрут для полного (перманентного) удаления сервера и связанных ВМ
@app.route('/permanent_delete_server/<int:server_id>')
def permanent_delete_server(server_id):
    data = load_data()
    # Удаляем сервер из списка
    data["servers"] = [s for s in data["servers"] if s["id"] != server_id]
    save_data(data)
    return redirect('/admin')

# Маршрут для просмотра сервера (без редактирования)
@app.route('/view_server/<int:server_id>')
def view_server(server_id):
    data = load_data()
    server = next((s for s in data["servers"] if s["id"] == server_id and not s.get("deleted", False)), None)
    if not server:
        return "Сервер не найден", 404

    # Берём все виртуальные машины, где deleted == False
    vms = [vm for vm in server.get("virtual_machines", []) if not vm.get("deleted", False)]
    used_cpu = sum(vm['cpu'] for vm in vms)
    used_ram = sum(vm['ram'] for vm in vms)
    used_ssd = sum(vm['ssd'] for vm in vms)
    used_hdd = sum(vm['hdd'] for vm in vms)
    free_cpu = server['cpu'] - used_cpu
    free_ram = server['ram'] - used_ram
    free_ssd = server['ssd'] - used_ssd
    free_hdd = server['hdd'] - used_hdd

    return render_template('view_server.html', server=server, virtual_machines=vms, 
                           used_resources={'used_cpu': used_cpu, 'used_ram': used_ram, 
                                           'used_ssd': used_ssd, 'used_hdd': used_hdd},
                           free_cpu=free_cpu, free_ram=free_ram, free_ssd=free_ssd, free_hdd=free_hdd)

# -------------------- Виртуальные машины --------------------

# Маршрут для добавления новой виртуальной машины
@app.route('/add_vm/<int:server_id>', methods=['POST'])
def add_vm(server_id):
    data = load_data()
    server = next((s for s in data["servers"] if s["id"] == server_id), None)
    if not server:
        return "Server not found", 404

    new_vm = {
        "id": get_next_vm_id(data),
        "name": request.form['name'],
        "cpu": int(request.form['cpu']),
        "ram": int(request.form['ram']),
        "ssd": int(request.form['ssd']),
        "hdd": int(request.form['hdd']),
        "deleted": False,
        "pending_delete": False,
        "server_id": server_id
    }
    server.setdefault("virtual_machines", []).append(new_vm)
    save_data(data)
    return redirect(f'/edit_server/{server_id}')

# Маршрут для пометки ВМ как "в ожидании удаления"
@app.route('/pending_delete_vm/<int:vm_id>')
def pending_delete_vm(vm_id):
    data = load_data()
    server_id = None
    for server in data["servers"]:
        for vm in server.get("virtual_machines", []):
            if vm["id"] == vm_id:
                vm["pending_delete"] = True
                server_id = server["id"]
                break
        if server_id is not None:
            break
    if server_id is None:
        return "VM not found", 404
    save_data(data)
    return redirect(f'/edit_server/{server_id}')

# Маршрут для отмены пометки удаления ВМ
@app.route('/cancel_delete_vm/<int:vm_id>')
def cancel_delete_vm(vm_id):
    data = load_data()
    server_id = None
    for server in data["servers"]:
        for vm in server.get("virtual_machines", []):
            if vm["id"] == vm_id:
                vm["pending_delete"] = False
                server_id = server["id"]
                break
        if server_id is not None:
            break
    if server_id is None:
        return "VM not found", 404
    save_data(data)
    return redirect(f'/edit_server/{server_id}')

# Маршрут для полного удаления виртуальной машины
@app.route('/permanent_delete_vm/<int:vm_id>')
def permanent_delete_vm(vm_id):
    data = load_data()
    server_id = None
    for server in data["servers"]:
        vms = server.get("virtual_machines", [])
        for i, vm in enumerate(vms):
            if vm["id"] == vm_id:
                server_id = server["id"]
                del vms[i]
                break
        if server_id is not None:
            break
    if server_id is None:
        return "VM not found", 404
    save_data(data)
    return redirect(f'/edit_server/{server_id}')

# Маршрут для восстановления виртуальной машины (снимаем флаг deleted)
@app.route('/restore_vm/<int:vm_id>')
def restore_vm(vm_id):
    data = load_data()
    server_id = None
    for server in data["servers"]:
        for vm in server.get("virtual_machines", []):
            if vm["id"] == vm_id:
                vm["deleted"] = False
                server_id = server["id"]
                break
        if server_id is not None:
            break
    if server_id is None:
        return "VM not found", 404
    save_data(data)
    return redirect(f'/edit_server/{server_id}')

# Маршрут для редактирования виртуальной машины (GET и POST)
@app.route('/edit_vm/<int:vm_id>', methods=['GET', 'POST'])
def edit_vm(vm_id):
    data = load_data()
    target_vm = None
    target_server = None
    for server in data["servers"]:
        for vm in server.get("virtual_machines", []):
            if vm["id"] == vm_id:
                target_vm = vm
                target_server = server
                break
        if target_vm is not None:
            break

    if not target_vm:
        return "VM not found", 404

    if request.method == 'POST':
        target_vm["name"] = request.form['name']
        target_vm["cpu"] = int(request.form['cpu'])
        target_vm["ram"] = int(request.form['ram'])
        target_vm["ssd"] = int(request.form['ssd'])
        target_vm["hdd"] = int(request.form['hdd'])
        save_data(data)
        return redirect(f'/edit_server/{target_server["id"]}')
    return render_template('edit_vm.html', vm=target_vm, server_id=target_server["id"])

# -------------------- Запуск приложения --------------------

if __name__ == '__main__':
    app.run(debug=True)

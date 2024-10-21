from flask import Flask, render_template, request, redirect
import pymysql

app = Flask(__name__)

def connect_db():
    return pymysql.connect(
        host='localhost',
        user='SERVERMANAGER',
        password='SUPERPASSWORD',
        db='SERVERMANAGER',
        cursorclass=pymysql.cursors.DictCursor
    )


# Главная страница - список серверов (только просмотр)
@app.route('/')
def index():
    conn = connect_db()
    cur = conn.cursor()

    # Получаем список серверов
    cur.execute("SELECT * FROM servers WHERE deleted = FALSE")
    servers = cur.fetchall()

    servers_with_resources = []
    
    # Для каждого сервера вычисляем использованные ресурсы
    for server in servers:
        server_id = server['id']

        # Получаем виртуальные машины для сервера
        cur.execute("SELECT * FROM virtual_machines WHERE server_id = %s AND deleted = FALSE", (server_id,))
        virtual_machines = cur.fetchall()

        # Считаем использованные ресурсы
        used_cpu = sum([vm['cpu'] for vm in virtual_machines])
        used_ram = sum([vm['ram'] for vm in virtual_machines])
        used_ssd = sum([vm['ssd'] for vm in virtual_machines])
        used_hdd = sum([vm['hdd'] for vm in virtual_machines])

        # Свободные ресурсы
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

    conn.close()

    return render_template('index.html', servers=servers_with_resources)

# Страница администрирования серверов
@app.route('/admin')
def admin():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM servers")
    servers = cur.fetchall()

    conn.close()
    return render_template('admin.html', servers=servers)

# Маршрут для добавления нового сервера
@app.route('/add_server', methods=['POST'])
def add_server():
    name = request.form['name']
    cpu = request.form['cpu']
    ram = request.form['ram']
    ssd = request.form['ssd']
    hdd = request.form['hdd']

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("INSERT INTO servers (name, cpu, ram, ssd, hdd) VALUES (%s, %s, %s, %s, %s)", 
                (name, cpu, ram, ssd, hdd))
    conn.commit()
    conn.close()

    return redirect('/admin')

# Маршрут для редактирования сервера
@app.route('/edit_server/<int:server_id>', methods=['GET', 'POST'])
def edit_server(server_id):
    conn = connect_db()
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        cpu = request.form['cpu']
        ram = request.form['ram']
        ssd = request.form['ssd']
        hdd = request.form['hdd']

        cur.execute("UPDATE servers SET name = %s, cpu = %s, ram = %s, ssd = %s, hdd = %s WHERE id = %s", 
                    (name, cpu, ram, ssd, hdd, server_id))
        conn.commit()
        conn.close()

        return redirect('/admin')
    else:
        cur.execute("SELECT * FROM servers WHERE id = %s", (server_id,))
        server = cur.fetchone()

        cur.execute("SELECT * FROM virtual_machines WHERE server_id = %s AND deleted = FALSE", (server_id,))
        virtual_machines = cur.fetchall()

        conn.close()

        return render_template('server_details.html', server=server, virtual_machines=virtual_machines)

# Маршрут для удаления сервера (помечаем как удалённый)
@app.route('/delete_server/<int:server_id>')
def delete_server(server_id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("UPDATE servers SET deleted = TRUE WHERE id = %s", (server_id,))
    conn.commit()
    conn.close()

    return redirect('/admin')

# Маршрут для восстановления сервера
@app.route('/restore_server/<int:server_id>')
def restore_server(server_id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("UPDATE servers SET deleted = FALSE WHERE id = %s", (server_id,))
    conn.commit()
    conn.close()

    return redirect('/admin')

@app.route('/permanent_delete_server/<int:server_id>')
def permanent_delete_server(server_id):
    conn = connect_db()
    cur = conn.cursor()

    # Удаление всех виртуальных машин, связанных с сервером
    cur.execute("DELETE FROM virtual_machines WHERE server_id = %s", (server_id,))
    conn.commit()

    # Полное удаление сервера
    cur.execute("DELETE FROM servers WHERE id = %s", (server_id,))
    conn.commit()

    conn.close()

    return redirect('/admin')

# Маршрут для просмотра сервера (без редактирования)
@app.route('/view_server/<int:server_id>')
def view_server(server_id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM servers WHERE id = %s AND deleted = FALSE", (server_id,))
    server = cur.fetchone()

    if not server:
        return "Сервер не найден", 404

    cur.execute("SELECT * FROM virtual_machines WHERE server_id = %s AND deleted = FALSE", (server_id,))
    virtual_machines = cur.fetchall()

    # Подсчитываем использование ресурсов
    used_cpu = sum([vm['cpu'] for vm in virtual_machines])
    used_ram = sum([vm['ram'] for vm in virtual_machines])
    used_ssd = sum([vm['ssd'] for vm in virtual_machines])
    used_hdd = sum([vm['hdd'] for vm in virtual_machines])

    # Рассчёт свободных ресурсов
    free_cpu = server['cpu'] - used_cpu
    free_ram = server['ram'] - used_ram
    free_ssd = server['ssd'] - used_ssd
    free_hdd = server['hdd'] - used_hdd

    # Передаём использованные и свободные ресурсы в шаблон
    return render_template('view_server.html', server=server, virtual_machines=virtual_machines, 
                           used_resources={'used_cpu': used_cpu, 'used_ram': used_ram, 
                                           'used_ssd': used_ssd, 'used_hdd': used_hdd},
                           free_cpu=free_cpu, free_ram=free_ram, free_ssd=free_ssd, free_hdd=free_hdd)

    conn.close()

    return render_template('view_server.html', server=server, virtual_machines=virtual_machines, used_resources=used_resources)

# Маршрут для добавления новой виртуальной машины
@app.route('/add_vm/<int:server_id>', methods=['POST'])
def add_vm(server_id):
    name = request.form['name']
    cpu = request.form['cpu']
    ram = request.form['ram']
    ssd = request.form['ssd']
    hdd = request.form['hdd']

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("INSERT INTO virtual_machines (name, cpu, ram, ssd, hdd, server_id) VALUES (%s, %s, %s, %s, %s, %s)", 
                (name, cpu, ram, ssd, hdd, server_id))
    conn.commit()
    conn.close()

    return redirect(f'/edit_server/{server_id}')

# Маршрут для помечания ВМ "в ожидании удаления"
@app.route('/pending_delete_vm/<int:vm_id>')
def pending_delete_vm(vm_id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT server_id FROM virtual_machines WHERE id = %s", (vm_id,))
    server_id = cur.fetchone()['server_id']

    # Помечаем виртуальную машину как "в ожидании удаления"
    cur.execute("UPDATE virtual_machines SET pending_delete = TRUE WHERE id = %s", (vm_id,))
    conn.commit()
    conn.close()

    return redirect(f'/edit_server/{server_id}')

# Маршрут для отмены удаления ВМ
@app.route('/cancel_delete_vm/<int:vm_id>')
def cancel_delete_vm(vm_id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT server_id FROM virtual_machines WHERE id = %s", (vm_id,))
    server_id = cur.fetchone()['server_id']

    # Снимаем флаг "в ожидании удаления"
    cur.execute("UPDATE virtual_machines SET pending_delete = FALSE WHERE id = %s", (vm_id,))
    conn.commit()
    conn.close()

    return redirect(f'/edit_server/{server_id}')

# Маршрут для полного удаления ВМ
@app.route('/permanent_delete_vm/<int:vm_id>')
def permanent_delete_vm(vm_id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT server_id FROM virtual_machines WHERE id = %s", (vm_id,))
    server_id = cur.fetchone()['server_id']

    # Полностью удаляем виртуальную машину
    cur.execute("DELETE FROM virtual_machines WHERE id = %s", (vm_id,))
    conn.commit()
    conn.close()

    return redirect(f'/edit_server/{server_id}')

# Маршрут для восстановления ВМ
@app.route('/restore_vm/<int:vm_id>')
def restore_vm(vm_id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT server_id FROM virtual_machines WHERE id = %s", (vm_id,))
    server_id = cur.fetchone()['server_id']

    cur.execute("UPDATE virtual_machines SET deleted = FALSE WHERE id = %s", (vm_id,))
    conn.commit()
    conn.close()

    return redirect(f'/edit_server/{server_id}')

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/edit_vm/<int:vm_id>', methods=['GET', 'POST'])
def edit_vm(vm_id):
    conn = connect_db()
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        cpu = request.form['cpu']
        ram = request.form['ram']
        ssd = request.form['ssd']
        hdd = request.form['hdd']

        cur.execute("UPDATE virtual_machines SET name = %s, cpu = %s, ram = %s, ssd = %s, hdd = %s WHERE id = %s",
                    (name, cpu, ram, ssd, hdd, vm_id))
        conn.commit()
        conn.close()

        return redirect(f'/edit_server/{vm_id}')  # Переход после сохранения

    cur.execute("SELECT * FROM virtual_machines WHERE id = %s", (vm_id,))
    vm = cur.fetchone()
    conn.close()


    return render_template('edit_vm.html', vm=vm)

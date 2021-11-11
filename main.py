from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
import time

app = Flask(__name__)
app.secret_key = 'some secret salt'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wh.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
manager = LoginManager(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    role =  db.Column(db.Integer)
    name = db.Column(db.String(128))
    last_name = db.Column(db.String(128))
    whs_id = db.Column(db.Integer)
    id_Admin = db.Column(db.Integer)

    def __repr__(self):
        return self.name

class Role(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name_role = db.Column(db.String(128), nullable=False, unique=True)


class Creat_warehouse(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name_wh = db.Column(db.String(128), nullable=False)
    id_Admin = db.Column(db.Integer)

    def __repr__(self):
        return self.name_wh


class Creat_product(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name_pt = db.Column(db.String(128), nullable=False, unique=True)
    article = db.Column(db.Integer, nullable=False, unique=True)
    qr = db.Column(db.Integer, nullable=False, unique=True)
    suitability = db.Column(db.Integer)
    units = db.Column(db.String(30))
    buy_price = db.Column(db.Integer)
    sell_price = db.Column(db.Integer)
    id_Admin = db.Column(db.Integer)
    marge = db.column_property(sell_price - buy_price)
    def __repr__(self):
        return self.name_pt


class Suppliers(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    id_Admin = db.Column(db.Integer)
    name_sl = db.Column(db.String(128), nullable=False, unique=True)
    phone = db.Column(db.Integer)
    def __repr__(self):
        return self.name_sl


class Stock(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    id_wh = db.Column(db.Integer, nullable=False)
    id_pt = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)


class Deliveries(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    id_wh = db.Column(db.Integer, nullable=False)
    id_manager = db.Column(db.Integer, nullable=False)
    datetime = db.Column(db.Integer)
    provider = db.Column(db.Integer)

class Deliveries_pt(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    id_deliveries = db.Column(db.Integer, nullable=False)
    id_pt = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)


class Shipment(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    id_wh = db.Column(db.Integer, nullable=False)
    id_manager = db.Column(db.Integer, nullable=False)
    datetime = db.Column(db.Integer)

class Shipment_pt(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    id_shipment = db.Column(db.Integer, nullable=False)
    id_pt = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)


class Debiting(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    id_wh = db.Column(db.Integer, nullable=False)
    id_manager = db.Column(db.Integer, nullable=False)
    datetime = db.Column(db.Integer)

class Debiting_pt(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    id_debiting = db.Column(db.Integer, nullable=False)
    id_pt = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)


class Inventory(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    id_wh = db.Column(db.Integer, nullable=False)
    id_manager = db.Column(db.Integer, nullable=False)
    datetime = db.Column(db.Integer)

class Inventory_pt(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    id_inventory = db.Column(db.Integer, nullable=False)
    id_pt = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    quantity_sys = db.Column(db.Integer, nullable=False)
    difference = db.column_property(quantity_sys - quantity)


class Orders(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    id_wh = db.Column(db.Integer, nullable=False)
    id_suppliers = db.Column(db.Integer, nullable=False)
    id_manager = db.Column(db.Integer, nullable=False)
    id_Admin = db.Column(db.Integer, nullable=False)
    datetime = db.Column(db.Integer)

class Orders_pt(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    id_order = db.Column(db.Integer, nullable=False)
    id_pt = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

db.create_all()

@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/admin/')
@login_required
def admin():
    if (current_user.role == 1):
        id_Admin = current_user.id
    else: id_Admin = current_user.id_Admin

    role = db.session.query(User, Role).join(Role, User.role==Role.id).filter(User.id==current_user.id).first()
    role = role.Role.name_role

    income_data = db.session.query(Creat_warehouse, Shipment, Shipment_pt) \
        .join(Shipment, Shipment.id_wh == Creat_warehouse.id) \
        .join(Shipment_pt, Shipment_pt.id_shipment == Shipment.id) \
        .join(Creat_product, Creat_product.id == Shipment_pt.id_pt) \
        .filter(Creat_warehouse.id_Admin == id_Admin)

    pts = Creat_product.query.filter_by(id_Admin=id_Admin).all()

    current_time = time.time()
    day = 86400
    income_week_time = {}
    for i in range(7, 0, -1):
        income = 0
        for pt in pts:
            res = income_data.add_columns(db.func.sum(Shipment_pt.id_pt).label('summ')).filter(Creat_product.id == pt.id)\
                .filter(Creat_product.id_Admin==id_Admin)\
                .filter(Shipment.datetime > current_time-round(current_time%day)-i*day)\
                .filter(Shipment.datetime < current_time-round(current_time%day)-(i-1)*day)
            if res[0].summ != None:
                income += Creat_product.query.filter(Creat_product.id == pt.id).first().marge * res[0].summ
        income_week_time[current_time-i*day] = income
    return render_template('admin.html', role=role, income=income_week_time, time=time)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    login = request.form.get('login')
    password = request.form.get('password')

    if login and password:
        user = User.query.filter_by(login=login).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            # --------- разобраться с next page ----------
            # next_page = request.args.get('next')
            # return redirect(next_page)
            return redirect(url_for('admin'))
        else:
            flash('Login or password is not correct')
    else:
        flash('Please fill login and password fields')
    return render_template('forms/form_authorization.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    name = request.form.get('name')
    login = request.form.get('login')
    password = request.form.get('password')
    password2 = request.form.get('password2')

    if request.method == 'POST':
        if not (login or password or password2):
            flash('Please, fill all fields!')
        elif password != password2:
            flash('Passwords are not equal!')
        else:
            hash_pwd = generate_password_hash(password)
            new_user = User(login=login, password=hash_pwd, role=1, name=name)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login_page'))
    return render_template('forms/form_register.html')


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# @app.after_request
# def redirect_to_signin(response):
#     if response.status_code == 401:
#         return redirect(url_for('login_page') + '?next=' + request.url)
#     return response

@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login_page'))
    return response


@app.route('/warehouse')
@login_required
def warehouse():
    if (current_user.role == 1):
        id_Admin = current_user.id
    else: id_Admin = current_user.id_Admin

    data = Creat_warehouse.query.filter_by(id_Admin=id_Admin).all()
    return render_template('warehouse.html', data=data)


@app.route('/warehouse/form_creat_warehouse', methods=['GET', 'POST'])
@login_required
def form_creat_warehouse():
    if (current_user.role == 1):
        id_Admin = current_user.id
    else: id_Admin = current_user.id_Admin

    name = request.form.get('name_wh')
    if request.method == 'POST':
        if not (name):
            flash('Please, fill all fields!')
        else:
            new_warehouse = Creat_warehouse(name_wh=name, id_Admin=id_Admin)
            db.session.add(new_warehouse)
            db.session.commit()
            return redirect(url_for('successfull_warehouse'))
    return render_template('forms/form_creat_warehouse.html')



@app.route('/warehouse/warehouse_view/<int:wh_id>')
@login_required
def warehouse_view(wh_id):
    pts = db.session.query(Stock, Creat_product)\
        .join(Creat_product, Stock.id_pt == Creat_product.id)\
        .filter(Stock.id_wh == wh_id).all()
    name = Creat_warehouse.query.filter_by(id=wh_id).first()
    return render_template('warehouse_view.html', name=name, pts=pts, wh_id=wh_id)


@app.route('/warehouse/warehouse_view/form_deliveries/<int:wh_id>', methods=['GET', 'POST'])
@login_required
def form_deliveries(wh_id):
    if (current_user.role == 1):
        id_Admin = current_user.id
    else: id_Admin = current_user.id_Admin

    pts = Creat_product.query.filter_by(id_Admin=id_Admin).all()
    spls = Suppliers.query.filter_by(id_Admin=id_Admin).all()
    cur_time = round(time.time())
    id_deliv = len(Deliveries.query.all()) + 1 #проверить правильно ли высчитывается id (не учитываются удалённые записи)

    supplier = request.form.get('supplier')
    products = request.form.getlist('products')
    quantity = request.form.getlist('quantity')

    if request.method == 'POST':
        if not (products or supplier or quantity):
            flash('Пожайлуста, заполните все поля!')
        else:
            new_deliveries = Deliveries(id_wh=wh_id, id_manager=current_user.id, datetime=cur_time, provider=supplier)
            db.session.add(new_deliveries)
            db.session.commit()
            for i in range(len(products)):
                new_deliveries_pt = Deliveries_pt(id_pt=products[i], id_deliveries=id_deliv, quantity=quantity[i])
                if Stock.query.filter_by(id_pt=products[i]).filter_by(id_wh=wh_id).first():
                    stock = Stock.query.filter_by(id_pt=products[i]).filter_by(id_wh=wh_id).first()
                    stock.quantity += int(quantity[i])
                    db.session.commit()
                else:
                    new_stock = Stock(id_wh=wh_id, id_pt=products[i], quantity=quantity[i])
                    db.session.add(new_stock)

                db.session.add(new_deliveries_pt)
                db.session.commit()
            return redirect(url_for('successfull_delivery'))
    return render_template('forms/form_deliveries.html', wh_id=wh_id, spls=spls, pts=pts)


@app.route('/warehouse/warehouse_view/form_shipment/<int:wh_id>', methods=['GET', 'POST'])
@login_required
def form_shipment(wh_id):
    pts = db.session.query(Stock, Creat_product).join(Creat_product, Stock.id_pt == Creat_product.id).filter(
        Stock.id_wh == wh_id).all()
    cur_time = round(time.time())
    id_ship = len(Shipment.query.all()) + 1

    products = request.form.getlist('products')
    quantity = request.form.getlist('quantity')

    if request.method == 'POST':
        if not (products or quantity):
            flash('Пожайлуста, заполните все поля!')
        else:
            new_shipment = Shipment(id_wh=wh_id, id_manager=current_user.id, datetime=cur_time)
            db.session.add(new_shipment)
            db.session.commit()
            for i in range(len(products)):
                new_shipment_pt = Shipment_pt(id_pt=products[i], id_shipment=id_ship, quantity=quantity[i])
                db.session.add(new_shipment_pt)
                db.session.commit()
                if Stock.query.filter_by(id_pt=products[i]).filter_by(id_wh=wh_id).first().quantity < int(quantity[i]):
                    flash('Количество товара превышает количество товара на складе! ')
                    return redirect(url_for('form_shipment', wh_id=wh_id))
                else:
                    stock = Stock.query.filter_by(id_pt=products[i]).filter_by(id_wh=wh_id).first()
                    stock.quantity -= int(quantity[i])
                    db.session.commit()
            return redirect(url_for('successfull_shipment'))
    return render_template('forms/form_shipment.html', wh_id=wh_id, pts=pts)


@app.route('/warehouse/warehouse_view/form_debiting/<int:wh_id>', methods=['GET', 'POST'])
@login_required
def form_debiting(wh_id):
    pts = db.session.query(Stock, Creat_product).join(Creat_product, Stock.id_pt == Creat_product.id).filter(Stock.id_wh == wh_id).all()
    cur_time = round(time.time())
    id_deb = len(Debiting.query.all()) + 1

    products = request.form.getlist('products')
    quantity = request.form.getlist('quantity')

    if request.method == 'POST':
        if not (products or quantity):
            flash('Пожайлуста, заполните все поля!')
        else:
            new_debiting = Debiting(id_wh=wh_id, id_manager=current_user.id, datetime=cur_time)
            db.session.add(new_debiting)
            db.session.commit()
            for i in range(len(products)):
                new_debiting_pt = Debiting_pt(id_pt=products[i], id_debiting=id_deb, quantity=quantity[i])
                db.session.add(new_debiting_pt)
                db.session.commit()
                if Stock.query.filter_by(id_pt=products[i]).filter_by(id_wh=wh_id).first().quantity < int(quantity[i]):
                    flash('Количество товара превышает количество товара на складе! ')
                    return redirect(url_for('form_debiting', wh_id=wh_id))
                else:
                    stock = Stock.query.filter_by(id_pt=products[i]).filter_by(id_wh=wh_id).first()
                    stock.quantity -= int(quantity[i])
                    db.session.commit()
            return redirect(url_for('successfull_debiting'))
    return render_template('forms/form_debiting.html', wh_id=wh_id, pts=pts)


@app.route('/warehouse/warehouse_view/form_inventory/<int:wh_id>', methods=['GET', 'POST'])
@login_required
def form_inventory(wh_id):
    pts = db.session.query(Stock, Creat_product)\
        .join(Creat_product, Stock.id_pt == Creat_product.id)\
        .filter(Stock.id_wh == wh_id).all()
    cur_time = round(time.time())
    id_invent = len(Inventory.query.all()) + 1

    products = request.form.getlist('products')
    quantity = request.form.getlist('quantity')

    if request.method == 'POST':
        if not (products or quantity):
            flash('Пожайлуста, заполните все поля!')
            return redirect(url_for('form_inventory', wh_id=wh_id))
        else:
            new_inventory = Inventory(id_wh=wh_id, id_manager=current_user.id, datetime=cur_time)
            db.session.add(new_inventory)
            db.session.commit()
            for i in range(len(products)):
                quantity_sys = Stock.query.filter_by(id_pt=products[i]).\
                                            filter_by(id_wh=wh_id).first().quantity
                new_inventory_pt = Inventory_pt(id_pt=products[i], id_inventory=id_invent,
                                                quantity=quantity[i], quantity_sys=quantity_sys)
                db.session.add(new_inventory_pt)
                db.session.commit()
                if quantity_sys != int(quantity[i]):
                    stock = Stock.query.filter_by(id_pt=products[i]).filter_by(id_wh=wh_id).first()
                    stock.quantity = int(quantity[i])
                    db.session.commit()
            return redirect(url_for('successfull_inventory'))
    return render_template('forms/form_inventory.html', wh_id=wh_id, pts=pts)




@app.route('/product_manage')
@login_required
def product_manage():
    if (current_user.role == 1):
        id_Admin = current_user.id
    else: id_Admin = current_user.id_Admin

    data = Creat_product.query.filter_by(id_Admin=id_Admin).all()
    return render_template('product_manage.html', data=data)


@app.route('/product_manage/form_creat_product', methods=['GET', 'POST'])
@login_required
def form_creat_product():
    if (current_user.role == 1):
        id_Admin = current_user.id
    else: id_Admin = current_user.id_Admin

    name = request.form.get('product_mame')
    article_pr = request.form.get('product_article')
    qr = request.form.get('product_qr')
    suitability = request.form.get('product_suitability')
    units = request.form.get('product_units')
    buy_price = request.form.get('buy_price')
    sell_price = request.form.get('sell_price')
    if request.method == 'POST':
        if not (name):
            flash('Please, fill all fields!')
        else:
            new_product = Creat_product(name_pt=name, article=article_pr,
                                        qr=qr, suitability=suitability, units=units,
                                        buy_price=buy_price, sell_price=sell_price, id_Admin=id_Admin)
            db.session.add(new_product)
            db.session.commit()
            return redirect(url_for('successfull_product'))
    return render_template('forms/form_creat_product.html')


@app.route('/suppliers')
@login_required
def suppliers():
    if (current_user.role == 1):
        id_Admin = current_user.id
    else:
        id_Admin = current_user.id_Admin

    data = Suppliers.query.filter_by(id_Admin=id_Admin).all()
    return render_template('suppliers.html', data=data)

@app.route('/suppliers/form_creat_supplier', methods=['GET', 'POST'])
@login_required
def form_creat_supplier():
    if (current_user.role == 1):
        id_Admin = current_user.id
    else:
        id_Admin = current_user.id_Admin
    name = request.form.get('name_sup')
    phone = request.form.get('phone')
    if request.method == 'POST':
        if not (name):
            flash('Пожайлуста, заполните все поля!')
            return redirect(url_for('form_creat_supplier'))
        else:
            new_supplier = Suppliers(name_sl=name, id_Admin=id_Admin, phone=phone)
            db.session.add(new_supplier)
            db.session.commit()
            return redirect(url_for('successfull_supplier'))
    return render_template('forms/form_creat_supplier.html')



@app.route('/employees')
@login_required
def employees():
    if (current_user.role == 1):
        id_Admin = current_user.id
    else:
        return redirect(url_for('admin'))
    # data = User.query.filter_by(id_Admin=id_Admin).all()
    data = db.session.query(User, Role, Creat_warehouse).join(Role, User.role==Role.id).join(Creat_warehouse,
                            User.whs_id==Creat_warehouse.id).filter(User.id_Admin==id_Admin).all()
    return render_template('employees.html', data=data)

@app.route('/orders')
@login_required
def orders():
    if (current_user.role == 1):
        id_Admin = current_user.id
    else:
        id_Admin = current_user.id_Admin
    data = db.session.query(Orders, Suppliers, User).join(Suppliers, Orders.id_suppliers == Suppliers.id)\
        .join(User, Orders.id_manager==User.id).filter(Orders.id_Admin == id_Admin).all()
    return render_template('orders.html', data=data, time=time)

@app.route('/orders/order_view/<int:id_order>')
@login_required
def order_view(id_order):
    ords = db.session.query(Orders_pt, Creat_product).join(Creat_product, Orders_pt.id_pt == Creat_product.id).filter(
        Orders_pt.id_order == id_order).all()
    return render_template('order_view.html', ords=ords, id_order=id_order)


@app.route('/orders/form_creat_order', methods=['GET', 'POST'])
@login_required
def form_creat_order():
    if (current_user.role == 1):
        id_Admin = current_user.id
    else:
        id_Admin = current_user.id_Admin
    pts = Creat_product.query.filter_by(id_Admin=id_Admin).all()
    whs = Creat_warehouse.query.filter_by(id_Admin=id_Admin).all()
    spls = Suppliers.query.all()
    cur_time = round(time.time())
    id_ord = len(Orders.query.all()) + 1

    wh_id = request.form.get('warehouses')
    supplier = request.form.get('supplier')
    products = request.form.getlist('products')
    quantity = request.form.getlist('quantity')

    if request.method == 'POST':
        if not (products or supplier or quantity):
            flash('Пожайлуста, заполните все поля!')
        else:
            new_order = Orders(id_wh=int(wh_id), id_manager=current_user.id, datetime=cur_time,
                               id_suppliers=int(supplier), id_Admin=id_Admin)
            db.session.add(new_order)
            db.session.commit()
            for i in range(len(products)):
                new_order_pt = Orders_pt(id_pt=products[i], id_order=id_ord, quantity=quantity[i])
                db.session.add(new_order_pt)
                db.session.commit()
            return redirect(url_for('successfull_order'))
    return render_template('forms/form_creat_order.html', pts=pts, spls=spls, whs=whs)



@app.route('/employees/form_creat_employees', methods=['GET', 'POST'])
@login_required
def form_creat_employees():
    roles = Role.query.filter(Role.id > 1).all()
    if (current_user.role == 1):
        id_Admin = current_user.id
    else: id_Admin = current_user.id_Admin
    wh = Creat_warehouse.query.filter_by(id_Admin=id_Admin).all()

    name = request.form.get('name_em')
    last_name = request.form.get('lname_em')
    role = request.form.get('role')
    warehouses = request.form.get('warehouses')
    # warehouses = request.form.getlist('warehouses')
    login = request.form.get('login')
    password = request.form.get('password')

    if request.method == 'POST':
        if not (login or password):
            flash('Please, fill all fields!')
        else:
            hash_pwd = generate_password_hash(password)
            new_employees = User(name=name, last_name=last_name,
                                 role=role, whs_id=warehouses, login=login,
                                 password=hash_pwd, id_Admin=id_Admin)
            db.session.add(new_employees)
            db.session.commit()
            return redirect(url_for('successfull_employees'))
    return render_template('forms/form_creat_employees.html', data=wh, role=roles)



@app.route('/reports')
@login_required
def reports():
    if (current_user.role == 1):
        id_Admin = current_user.id
    else:
        id_Admin = current_user.id_Admin

    deliv_data = db.session.query(Deliveries, Creat_warehouse, User, Suppliers)\
        .join(Creat_warehouse,Deliveries.id_wh == Creat_warehouse.id)\
        .join(User, Deliveries.id_manager==User.id)\
        .join(Suppliers, Deliveries.provider==Suppliers.id)\
        .filter(Creat_warehouse.id_Admin==id_Admin).all()

    del_pt = db.session.query(Deliveries_pt, Creat_product)\
        .join(Creat_product, Deliveries_pt.id_pt==Creat_product.id)\
        .filter(Creat_product.id_Admin==id_Admin).all()


    ship_data = db.session.query(Shipment, Creat_warehouse, User) \
        .join(Creat_warehouse, Shipment.id_wh == Creat_warehouse.id) \
        .join(User, Shipment.id_manager == User.id) \
        .filter(Creat_warehouse.id_Admin == id_Admin).all()

    ship_pt = db.session.query(Shipment_pt, Creat_product) \
        .join(Creat_product, Shipment_pt.id_pt == Creat_product.id) \
        .filter(Creat_product.id_Admin == id_Admin).all()


    invent_data = db.session.query(Inventory, Creat_warehouse, User) \
        .join(Creat_warehouse, Inventory.id_wh == Creat_warehouse.id) \
        .join(User, Inventory.id_manager == User.id) \
        .filter(Creat_warehouse.id_Admin == id_Admin).all()

    invent_pt = db.session.query(Inventory_pt, Creat_product) \
        .join(Creat_product, Inventory_pt.id_pt == Creat_product.id) \
        .filter(Creat_product.id_Admin == id_Admin).all()


    deb_data = db.session.query(Debiting, Creat_warehouse, User) \
        .join(Creat_warehouse, Debiting.id_wh == Creat_warehouse.id) \
        .join(User, Debiting.id_manager == User.id) \
        .filter(Creat_warehouse.id_Admin == id_Admin).all()

    deb_pt = db.session.query(Debiting_pt, Creat_product) \
        .join(Creat_product, Debiting_pt.id_pt == Creat_product.id) \
        .filter(Creat_product.id_Admin == id_Admin).all()

    income_data = db.session.query(Creat_warehouse, Shipment, Shipment_pt)\
        .join(Shipment, Shipment.id_wh==Creat_warehouse.id)\
        .join(Shipment_pt, Shipment_pt.id_shipment==Shipment.id) \
        .join(Creat_product, Creat_product.id == Shipment_pt.id_pt) \
        .filter(Creat_warehouse.id_Admin==id_Admin)

    whs = Creat_warehouse.query.filter_by(id_Admin=id_Admin).all()
    pts = Creat_product.query.filter_by(id_Admin=id_Admin).all()

    current_time = time.time()
    l_day = current_time - 86400
    l_mon = current_time - 7884000
    l_quarter = current_time - 23652000

    income_whs_day = {}
    income_whs_mon = {}
    income_whs_q = {}
    for wh in whs:
        income_wh = 0
        for pt in pts:
            res = income_data.add_columns(db.func.sum(Shipment_pt.id_pt).label('summ')).filter(
                Creat_warehouse.id == wh.id).filter(Creat_product.id == pt.id).filter(Shipment.datetime > l_day)
            if res[0].summ != None:
                income_wh += Creat_product.query.filter(Creat_product.id == pt.id).first().marge * res[0].summ
        income_whs_day[wh.name_wh] = income_wh

    for wh in whs:
        income_wh = 0
        for pt in pts:
            res = income_data.add_columns(db.func.sum(Shipment_pt.id_pt).label('summ')).filter(
                Creat_warehouse.id == wh.id).filter(Creat_product.id == pt.id).filter(Shipment.datetime > l_mon)
            if res[0].summ != None:
                income_wh += Creat_product.query.filter(Creat_product.id == pt.id).first().marge * res[0].summ
        income_whs_mon[wh.name_wh] = income_wh

    for wh in whs:
        income_wh = 0
        for pt in pts:
            res = income_data.add_columns(db.func.sum(Shipment_pt.id_pt).label('summ')).filter(
                Creat_warehouse.id == wh.id).filter(Creat_product.id == pt.id).filter(Shipment.datetime > l_quarter)
            if res[0].summ != None:
                income_wh += Creat_product.query.filter(Creat_product.id == pt.id).first().marge * res[0].summ
        income_whs_q[wh.name_wh] = income_wh


    return render_template('reports.html', deliv_data=deliv_data, del_pt=del_pt
                           , ship_data=ship_data, ship_pt=ship_pt
                           , invent_data=invent_data, invent_pt=invent_pt
                           , deb_data=deb_data, deb_pt=deb_pt
                           , income_data=income_data
                           , time=time, db=db
                           ,income_whs_day=income_whs_day, income_whs_mon=income_whs_mon,
                           income_whs_q=income_whs_q)


@app.route('/warehouse/form_creat_warehouse/successfull')
@login_required
def successfull_warehouse():
    return render_template('successfull/successfull_warehouse.html')


@app.route('/orders/form_creat_order/successfull')
@login_required
def successfull_order():
    return render_template('successfull/successfull_order.html')


@app.route('/warehouse/warehouse_view/successfull')
@login_required
def successfull_product():
    return render_template('successfull/successfull_product.html')


@app.route('/employees/form_creat_employees/successfull')
@login_required
def successfull_employees():
    return render_template('successfull/successfull_employees.html')


@app.route('/delivery/successfull')
@login_required
def successfull_delivery():
    return render_template('successfull/successfull_delivery.html')

@app.route('/shipment/successfull')
@login_required
def successfull_shipment():
    return render_template('successfull/successfull_shipment.html')

@app.route('/debiting/successfull')
@login_required
def successfull_debiting():
    return render_template('successfull/successfull_debiting.html')

@app.route('/inventory/successfull')
@login_required
def successfull_inventory():
    return render_template('successfull/successfull_inventory.html')

@app.route('/suppliers/successfull')
@login_required
def successfull_supplier():
    return render_template('successfull/successfull_supplier.html')


@app.route('/employees/<int:id_delete>')
@login_required
def delete_employees(id_delete):
    User.query.filter_by(id=id_delete).delete()
    db.session.commit()
    return redirect(url_for('employees'))


@app.route('/warehouse/<int:id_delete>')
@login_required
def delete_warehouse(id_delete):
    Creat_warehouse.query.filter_by(id=id_delete).delete()
    Stock.query.filter_by(id_wh=id_delete).delete()
    db.session.commit()
    return redirect(url_for('warehouse'))


@app.route('/orders/<int:id_delete>')
@login_required
def delete_order(id_delete):
    Orders.query.filter_by(id=id_delete).delete()
    Orders_pt.query.filter_by(id_order=id_delete).delete()
    db.session.commit()
    return redirect(url_for('orders'))

@app.route('/order_view/<int:id_delete>')
@login_required
def delete_order_view(id_delete):
    Orders_pt.query.filter_by(id_order=id_delete).delete()
    db.session.commit()
    return redirect(url_for('orders'))


@app.route('/suppliers/<int:id_delete>')
@login_required
def delete_supplier(id_delete):
    Suppliers.query.filter_by(id=id_delete).delete()
    db.session.commit()
    return redirect(url_for('suppliers'))


@app.route('/product_manage/<int:id_delete>')
@login_required
def delete_product(id_delete):
    Creat_product.query.filter_by(id=id_delete).delete()
    db.session.commit()
    return redirect(url_for('product_manage'))


if __name__ == '__main__':
    app.run(debug=True)

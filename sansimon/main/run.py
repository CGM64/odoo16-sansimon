# -*- coding: utf-8 -*-
import xmlrpc.client

class SanSimonOdoo(object):
    """docstring for ."""


#url = 'http://localhost:8013'
#db = 'Odoo13_SanSimonProd'
username = 'admin'
password = 's0p0rt3'
url = 'http://192.168.99.100:29013'
db = 'Odoo13_SansimonED'
datos = []
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

uid = common.authenticate(db, username, password, {})


#Sirve para setear un valor en la configuracion de la conta para volver a cargar la plantilla contable
#models.execute_kw(db, uid, password, 'account.account.template', 'actualizarPlantillaID', [[]])
#models.execute_kw(db, uid, password, 'account.chart.template', 'try_loading', [[]])

#Sirve para cargar el catalogo de productos
#models.execute_kw(db, uid, password, 'product.template', 'delete_all_date', [[]])
#models.execute_kw(db, uid, password, 'product.template', 'get_import_intelisis', [[]])

#Sirve para cargar el inventario de instelisis
#models.execute_kw(db, uid, password, 'stock.inventory', 'getInventoryIntelisis', [[]])

#Sirve para validar todos los movimientos de ajuste
models.execute_kw(db, uid, password, 'stock.inventory', 'validateStockInventory', [[]])

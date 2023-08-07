# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning

_logger = logging.getLogger(__name__)

EMPRESA = 'SANSI'
SUCURSAL = 901

UBICACION_PADRE = 7

class Inventory(models.Model):
    _inherit = 'stock.inventory'

    def getInventoryIntelisis(self):
        query = "spInvval"
        #params = ( '023674 32','1056 653','(TODOS)','Costo Promedio','12/31/2020',EMPRESA)
        params = ( '023674 32','VARIOS','(TODOS)','Costo Promedio','12/31/2020',EMPRESA)
        sql_server = self.env["connect.mssql"].search([],limit=1)
        #query = query % (EMPRESA,)
        res = sql_server.execute_proc(query, params)
        valuacion_inventario = []
        for row in res:
            valuacion_inventario.append(row)

        valuacion_inventario = sorted(valuacion_inventario, key=lambda k:k['Almacen'])
        self.insertStockInventory(valuacion_inventario)

        return True

    def insertStockInventory(self, inventario):
        nueva_linea_almacen = None
        i = 0
        stock_inventory = None
        for linea in inventario:
            i += 1

            ialmacen = linea['Almacen'].strip()
            almacen = self.ifExistAlmacen(ialmacen)

            if nueva_linea_almacen != almacen.id:
                new_inventario = {}
                new_inventario['name'] = "Inventario Inicial (%s)" % ialmacen
                new_inventario['company_id'] = self.env.user.company_id.id
                stock_inventory = self.env["stock.inventory"].create(new_inventario)
                #stock_inventory.action_start()
                nueva_linea_almacen = almacen.id

            if stock_inventory:

                product = self.env["product.product"].search([('default_code','=',linea['Articulo'].strip())])
                if product:
                    padre_location_id = self.env["stock.location"].search([("name",'=',ialmacen)])
                    padre_location_id = padre_location_id.id
                    ubicacion = self.env["stock.location"].search([("name",'=','Stock'),('usage','=','internal'),('location_id','=',padre_location_id)])
                    new_linea_inventario = {}
                    new_linea_inventario['inventory_id'] = stock_inventory.id
                    new_linea_inventario['product_id'] = product.id
                    new_linea_inventario['location_id'] = ubicacion.id
                    new_linea_inventario['product_qty'] = linea['Existencias']
                    new_linea_inventario['company_id'] = self.env.user.company_id.id
                    self.env["stock.inventory.line"].create(new_linea_inventario)


                else:
                    #raise UserError(_('El producto %s no existe') % linea['Articulo'])
                    _logger.warning(_('El producto %s no existe') % linea['Articulo'])

    def validateStockInventory(self):
        stock_inventory = self.env["stock.inventory"].search([('state','=','draft')])
        for inv in stock_inventory:
            _logger.warning(_('Validando inventario %s') % inv.name)
            inv.action_start()
            inv.action_validate()
        return True


    def ifExistAlmacen(self, almacen_code):
        almacen = self.env["stock.warehouse"].search([("name","=",almacen_code)])
        if not almacen:
            new_almacen = {}
            new_almacen['name'] = almacen_code
            new_almacen['code'] = almacen_code
            almacen = self.env["stock.warehouse"].create(new_almacen)
        return almacen

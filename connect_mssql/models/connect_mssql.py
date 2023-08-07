# -*- coding: utf-8 -*-
# Copyright 2019 Ehab Mosilhy (ehabmosilhy@gmail.com)

from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class ConnectMssql(models.Model):
    _name = "connect.mssql"
    _description = 'Connect to MS SQL Server'

    name = fields.Char("Descripcion", requiere=True)
    server_name = fields.Char('Server', required=True, help="The server name, could be an IP or a URL")
    database_name = fields.Char('Database name', required=True)
    user_name = fields.Char('User name', required=True)
    password = fields.Char('Password', required=True)
    query = fields.Text('SQL Query/Instruction', required=True,
                        help="A Select statement or an insert/update/delete instruction")
    result = fields.Text('Result')


    def test_execute_query(self):
        self.execute_query(self.query)

    def execute_query(self, query):
        try:
            import pymssql

            # Connection Parameters
            my_server = self.server_name
            my_user = self.user_name
            my_database = self.database_name
            my_password = self.password
            my_query = query


            # Make the connection and execute the query
            conn = pymssql.connect(server=my_server, user=my_user, password=my_password, database=my_database)
            cursor = conn.cursor(as_dict=True)
            cursor.execute(my_query)
            result = []
            for row in cursor:
                result.append(row)
            conn.close()
            return result

        except Exception as e:
            self.result = "An Error Occurred, please check your parameters!\n" \
                          "And make sure (pymssql) is installed (pip3 install pymssql)."
            _logger.exception(e)

    def execute_proc(self, query, params):
        result = []
        try:
            import pymssql

            # Connection Parameters
            my_server = self.server_name
            my_user = self.user_name
            my_database = self.database_name
            my_password = self.password
            my_query = query


            # Make the connection and execute the query
            conn = pymssql.connect(server=my_server, user=my_user, password=my_password, database=my_database)
            cursor = conn.cursor(as_dict=True)
            cursor.callproc(my_query, params)

            for row in cursor:
                result.append(row)
            conn.close()


        except Exception as e:
            self.result = "An Error Occurred, please check your parameters!\n" \
                          "And make sure (pymssql) is installed (pip3 install pymssql)."
            _logger.exception(e)

        return result



    def execute_update(self, query):
        try:
            import pymssql

            # Connection Parameters
            my_server = self.server_name
            my_user = self.user_name
            my_database = self.database_name
            my_password = self.password
            my_query = query


            # Make the connection and execute the query
            conn = pymssql.connect(server=my_server, user=my_user, password=my_password, database=my_database)
            cursor = conn.cursor()
            cursor.execute(my_query)

            # Check whether the query is a select statement or an insert/update/delete instruction
            if my_query.strip().split(" ")[0].lower() == "select":
                rows = cursor.fetchall()
                my_result = ""
                for i in rows:
                    for x in i:
                        my_result += "\t" + str(x)
                    my_result += "\n"

                # Show the result
                self.result = my_result
            else:
                conn.commit()
                self.result = "Statement executed successfully, please check your database or make a select statement."
            conn.close()

        except Exception as e:
            self.result = "An Error Occurred, please check your parameters!\n" \
                          "And make sure (pymssql) is installed (pip3 install pymssql)."
            _logger.exception(e)

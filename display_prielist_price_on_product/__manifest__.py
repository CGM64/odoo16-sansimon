# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Display Pricelist Price On Products",
  "summary"              :  """The module displays the every pricelist and corresponding price  to which the product is assigned to in the product form""",
  "category"             :  "Sales",
  "version"              :  "1.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Display-Pricelist-Price-On-Products.html",
  "description"          :  """Display Pricelist Price On Products
Pricelist Price On Products
Product Price On the basis of pricelist
Odoo Display Pricelist Price On Products
Show different pricelist in product from
Pricelist tab in product form
Product pricelists in product form
Odoo Pricelist prices in product form""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=display_pricelist_price_on_product",
  "depends"              :  ['sale'],
  "data"                 :  [
                             'views/pricelist_view.xml',
                             'views/product_view.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  49,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}
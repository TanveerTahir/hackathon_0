#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Odoo MCP Server

Provides MCP tools for Odoo ERP integration:
- Accounting (invoices, payments, journal entries)
- Partners (customers, vendors)
- Products/Services
- Financial Reports

Usage:
    python odoo_mcp_server.py
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv
from mcp.server import Server
import mcp.server.stdio

# Try to import xmlrpc client, provide fallback
try:
    import xmlrpc.client
except ImportError:
    xmlrpc = None

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('odoo-mcp-server')

# Configuration
ODOO_URL = os.getenv('ODOO_URL', 'http://localhost:8069')
ODOO_DB = os.getenv('ODOO_DB', 'hackathon_db')
ODOO_USERNAME = os.getenv('ODOO_USERNAME', 'admin')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'admin')

# Create server
server = Server('odoo-mcp-server')


class OdooClient:
    """Client for Odoo XML-RPC API"""

    def __init__(self, url: str, db: str, username: str, password: str):
        self.url = url.rstrip('/')
        self.db = db
        self.username = username
        self.password = password
        self.uid = None
        self.common = None
        self.models = None

        # Initialize connection
        self._connect()

    def _connect(self):
        """Establish connection to Odoo server"""
        if xmlrpc is None:
            raise ImportError(
                'xmlrpcclient2 not installed. Run: pip install xmlrpcclient2'
            )

        try:
            # Common endpoint for authentication
            self.common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')

            # Authenticate
            self.uid = self.common.authenticate(self.db, self.username, self.password, {})

            if not self.uid:
                raise Exception('Authentication failed. Check credentials.')

            # Models endpoint for data operations
            self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')

            logger.info(f'Connected to Odoo: {self.url} (DB: {self.db}, User: {self.username})')

        except Exception as e:
            logger.error(f'Failed to connect to Odoo: {str(e)}')
            raise

    def _execute(
        self,
        model: str,
        method: str,
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None
    ) -> Any:
        """Execute method on Odoo model"""
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}

        try:
            return self.models.executekw(
                self.db, self.uid, self.password,
                model, method, args, kwargs
            )
        except Exception as e:
            logger.error(f'Odoo execution error ({model}.{method}): {str(e)}')
            raise

    def search(
        self,
        model: str,
        domain: List[Any] = None,
        limit: int = 80,
        order: str = None,
        fields: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Search records in a model"""
        if domain is None:
            domain = []

        read_fields = fields if fields else ['id', 'name', 'create_date']

        ids = self._execute(
            model, 'search', [domain],
            {'limit': limit, 'order': order}
        )

        if not ids:
            return []

        return self._execute(model, 'read', [ids], {'fields': read_fields})

    def read(self, model: str, id: int, fields: List[str] = None) -> Optional[Dict[str, Any]]:
        """Read a single record"""
        result = self._execute(model, 'read', [[id]], {'fields': fields or []})
        return result[0] if result else None

    def create(self, model: str, values: Dict[str, Any]) -> int:
        """Create a new record"""
        return self._execute(model, 'create', [values])

    def write(self, model: str, id: int, values: Dict[str, Any]) -> bool:
        """Update an existing record"""
        return self._execute(model, 'write', [[id], values])

    def unlink(self, model: str, id: int) -> bool:
        """Delete a record"""
        return self._execute(model, 'unlink', [[id]])

    def get_invoices(
        self,
        state: str = None,
        move_type: str = None,
        partner_id: int = None,
        limit: int = 50,
        days: int = None
    ) -> List[Dict[str, Any]]:
        """Get customer invoices"""
        domain = []

        if state:
            domain.append(('state', '=', state))
        if move_type:
            domain.append(('move_type', '=', move_type))
        if partner_id:
            domain.append(('partner_id', '=', partner_id))
        if days:
            cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            domain.append(('invoice_date', '>=', cutoff))

        fields = [
            'id', 'name', 'partner_id', 'invoice_date', 'invoice_date_due',
            'amount_total', 'amount_residual', 'state', 'move_type',
            'payment_state', 'currency_id', 'company_id'
        ]

        return self.search('account.move', domain=domain, limit=limit, order='invoice_date desc', fields=fields)

    def create_invoice(
        self,
        partner_id: int,
        invoice_lines: List[Dict[str, Any]],
        invoice_date: str = None,
        invoice_date_due: str = None,
        move_type: str = 'out_invoice',
        narrative: str = None
    ) -> int:
        """Create a customer invoice"""
        values = {
            'move_type': move_type,
            'partner_id': partner_id,
            'invoice_line_ids': [(0, 0, line) for line in invoice_lines],
        }

        if invoice_date:
            values['invoice_date'] = invoice_date
        if invoice_date_due:
            values['invoice_date_due'] = invoice_date_due
        if narrative:
            values['narration'] = narrative

        return self.create('account.move', values)

    def validate_invoice(self, invoice_id: int) -> bool:
        """Validate (post) an invoice"""
        return self._execute('account.move', 'action_post', [[invoice_id]])

    def get_payments(
        self,
        state: str = None,
        partner_id: int = None,
        limit: int = 50,
        days: int = None
    ) -> List[Dict[str, Any]]:
        """Get payment records"""
        domain = []

        if state:
            domain.append(('state', '=', state))
        if partner_id:
            domain.append(('partner_id', '=', partner_id))
        if days:
            cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            domain.append(('date', '>=', cutoff))

        fields = [
            'id', 'name', 'partner_id', 'date', 'amount',
            'state', 'payment_type', 'payment_method_line_id'
        ]

        return self.search('account.payment', domain=domain, limit=limit, order='date desc', fields=fields)

    def register_payment(
        self,
        invoice_id: int,
        amount: float,
        payment_date: str = None,
        payment_method: str = 'manual'
    ) -> int:
        """Register payment for an invoice"""
        # Create payment record
        values = {
            'move_id': invoice_id,
            'amount': amount,
            'date': payment_date or datetime.now().strftime('%Y-%m-%d'),
            'payment_method_line_id': payment_method,
        }

        return self.create('account.payment', values)

    def get_account_moves(
        self,
        move_type: str = None,
        state: str = None,
        limit: int = 50,
        days: int = None
    ) -> List[Dict[str, Any]]:
        """Get journal entries"""
        domain = []

        if move_type:
            domain.append(('move_type', '=', move_type))
        if state:
            domain.append(('state', '=', state))
        if days:
            cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            domain.append(('date', '>=', cutoff))

        fields = [
            'id', 'name', 'date', 'move_type', 'state',
            'ref', 'amount_total', 'currency_id'
        ]

        return self.search('account.move', domain=domain, limit=limit, order='date desc', fields=fields)

    def create_account_move(
        self,
        name: str,
        move_type: str,
        date: str,
        line_ids: List[Dict[str, Any]],
        ref: str = None
    ) -> int:
        """Create a journal entry"""
        values = {
            'name': name,
            'move_type': move_type,
            'date': date,
            'line_ids': [(0, 0, line) for line in line_ids],
        }

        if ref:
            values['ref'] = ref

        return self.create('account.move', values)

    def get_partners(
        self,
        search_term: str = None,
        partner_type: str = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get business partners (customers/vendors)"""
        domain = []

        if search_term:
            domain.append('|', ('name', 'ilike', search_term), ('email', 'ilike', search_term))
        if partner_type:
            domain.append(('partner_type', '=', partner_type))

        fields = [
            'id', 'name', 'email', 'phone', 'mobile',
            'street', 'city', 'zip', 'country_id',
            'vat', 'partner_type', 'customer_rank', 'supplier_rank'
        ]

        return self.search('res.partner', domain=domain, limit=limit, fields=fields)

    def create_partner(
        self,
        name: str,
        email: str = None,
        phone: str = None,
        street: str = None,
        city: str = None,
        zip_code: str = None,
        country_id: int = None,
        vat: str = None,
        partner_type: str = 'both'
    ) -> int:
        """Create a new business partner"""
        values = {
            'name': name,
            'partner_type': partner_type,
        }

        if email:
            values['email'] = email
        if phone:
            values['phone'] = phone
        if street:
            values['street'] = street
        if city:
            values['city'] = city
        if zip_code:
            values['zip'] = zip_code
        if country_id:
            values['country_id'] = country_id
        if vat:
            values['vat'] = vat

        return self.create('res.partner', values)

    def get_products(
        self,
        search_term: str = None,
        product_type: str = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get products/services"""
        domain = []

        if search_term:
            domain.append('|', ('name', 'ilike', search_term), ('default_code', 'ilike', search_term))
        if product_type:
            domain.append(('type', '=', product_type))

        fields = [
            'id', 'name', 'default_code', 'type', 'list_price',
            'standard_price', 'uom_name', 'categ_id', 'description'
        ]

        return self.search('product.template', domain=domain, limit=limit, fields=fields)

    def get_financial_reports(
        self,
        report_type: str = 'balance_sheet',
        date_from: str = None,
        date_to: str = None
    ) -> Dict[str, Any]:
        """Get financial reports (P&L, Balance Sheet)"""
        # This is a simplified implementation
        # In production, you'd use Odoo's accounting reports module

        if report_type == 'profit_loss':
            return self._get_profit_loss(date_from, date_to)
        elif report_type == 'balance_sheet':
            return self._get_balance_sheet(date_to)
        else:
            return {'error': f'Unknown report type: {report_type}'}

    def _get_profit_loss(self, date_from: str = None, date_to: str = None) -> Dict[str, Any]:
        """Get Profit & Loss report"""
        # Simplified P&L calculation
        if not date_to:
            date_to = datetime.now().strftime('%Y-%m-%d')
        if not date_from:
            date_from = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

        # Get income and expense accounts
        income_moves = self._get_account_totals([('account_type', '=', 'income')], date_from, date_to)
        expense_moves = self._get_account_totals([('account_type', '=', 'expense')], date_from, date_to)

        total_income = sum(m.get('balance', 0) for m in income_moves)
        total_expense = sum(m.get('balance', 0) for m in expense_moves)

        return {
            'report_type': 'profit_loss',
            'date_from': date_from,
            'date_to': date_to,
            'total_income': total_income,
            'total_expense': total_expense,
            'net_profit': total_income - total_expense,
            'income_accounts': income_moves,
            'expense_accounts': expense_moves
        }

    def _get_balance_sheet(self, date: str = None) -> Dict[str, Any]:
        """Get Balance Sheet report"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')

        # Get asset and liability accounts
        asset_moves = self._get_account_totals([('account_type', '=', 'asset')], None, date)
        liability_moves = self._get_account_totals([('account_type', '=', 'liability')], None, date)
        equity_moves = self._get_account_totals([('account_type', '=', 'equity')], None, date)

        total_assets = sum(m.get('balance', 0) for m in asset_moves)
        total_liabilities = sum(m.get('balance', 0) for m in liability_moves)
        total_equity = sum(m.get('balance', 0) for m in equity_moves)

        return {
            'report_type': 'balance_sheet',
            'date': date,
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'total_equity': total_equity,
            'assets': asset_moves,
            'liabilities': liability_moves,
            'equity': equity_moves
        }

    def _get_account_totals(
        self,
        domain: List[Any],
        date_from: str = None,
        date_to: str = None
    ) -> List[Dict[str, Any]]:
        """Get account totals for report calculation"""
        # Simplified implementation
        return []

    def check_connection(self) -> Dict[str, Any]:
        """Check Odoo connection status"""
        try:
            # Get Odoo version
            version = self.common.version()

            # Get company info
            company = self.read('res.company', 1, ['name', 'currency_id'])

            return {
                'connected': True,
                'url': self.url,
                'database': self.db,
                'username': self.username,
                'uid': self.uid,
                'version': version,
                'company': company.get('name') if company else 'Unknown'
            }
        except Exception as e:
            return {
                'connected': False,
                'error': str(e)
            }


# Global client instance
odoo_client: Optional[OdooClient] = None


def get_client() -> OdooClient:
    """Get or create Odoo client instance"""
    global odoo_client
    if odoo_client is None:
        if not all([ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD]):
            raise Exception(
                'Odoo credentials not configured. '
                'Set ODOO_URL, ODOO_DB, ODOO_USERNAME, and ODOO_PASSWORD environment variables.'
            )
        try:
            odoo_client = OdooClient(
                url=ODOO_URL,
                db=ODOO_DB,
                username=ODOO_USERNAME,
                password=ODOO_PASSWORD
            )
        except Exception as e:
            logger.warning(f'Odoo client initialization failed: {e}')
            raise
    return odoo_client


@server.list_tools()
async def list_tools() -> List[Dict[str, Any]]:
    """List available Odoo tools"""
    return [
        {
            'name': 'odoo_connect',
            'description': 'Test connection to Odoo server and get connection info',
            'inputSchema': {
                'type': 'object',
                'properties': {}
            }
        },
        {
            'name': 'odoo_get_invoices',
            'description': 'Get customer invoices from Odoo accounting',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'state': {
                        'type': 'string',
                        'description': 'Filter by state (draft, posted, cancel)',
                        'enum': ['draft', 'posted', 'cancel']
                    },
                    'limit': {
                        'type': 'integer',
                        'description': 'Number of invoices to retrieve (default: 50)',
                        'default': 50
                    },
                    'days': {
                        'type': 'integer',
                        'description': 'Only invoices from last N days'
                    },
                    'partner_id': {
                        'type': 'integer',
                        'description': 'Filter by partner ID'
                    }
                }
            }
        },
        {
            'name': 'odoo_create_invoice',
            'description': 'Create a new customer invoice in Odoo',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'partner_id': {
                        'type': 'integer',
                        'description': 'Customer/partner ID'
                    },
                    'invoice_lines': {
                        'type': 'array',
                        'description': 'Invoice line items',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'product_id': {'type': 'integer'},
                                'name': {'type': 'string'},
                                'quantity': {'type': 'number'},
                                'price_unit': {'type': 'number'}
                            }
                        }
                    },
                    'invoice_date': {
                        'type': 'string',
                        'description': 'Invoice date (YYYY-MM-DD)'
                    },
                    'invoice_date_due': {
                        'type': 'string',
                        'description': 'Due date (YYYY-MM-DD)'
                    },
                    'narrative': {
                        'type': 'string',
                        'description': 'Invoice notes'
                    }
                },
                'required': ['partner_id', 'invoice_lines']
            }
        },
        {
            'name': 'odoo_validate_invoice',
            'description': 'Validate (post) a draft invoice',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'invoice_id': {
                        'type': 'integer',
                        'description': 'Invoice ID to validate'
                    }
                },
                'required': ['invoice_id']
            }
        },
        {
            'name': 'odoo_get_payments',
            'description': 'Get payment records from Odoo',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'state': {
                        'type': 'string',
                        'description': 'Filter by state',
                        'enum': ['draft', 'posted', 'cancelled']
                    },
                    'limit': {
                        'type': 'integer',
                        'description': 'Number of payments to retrieve (default: 50)',
                        'default': 50
                    },
                    'days': {
                        'type': 'integer',
                        'description': 'Only payments from last N days'
                    }
                }
            }
        },
        {
            'name': 'odoo_register_payment',
            'description': 'Register a payment for an invoice',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'invoice_id': {
                        'type': 'integer',
                        'description': 'Invoice ID'
                    },
                    'amount': {
                        'type': 'number',
                        'description': 'Payment amount'
                    },
                    'payment_date': {
                        'type': 'string',
                        'description': 'Payment date (YYYY-MM-DD)'
                    }
                },
                'required': ['invoice_id', 'amount']
            }
        },
        {
            'name': 'odoo_get_partners',
            'description': 'Search business partners (customers/vendors)',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'search_term': {
                        'type': 'string',
                        'description': 'Search by name or email'
                    },
                    'limit': {
                        'type': 'integer',
                        'description': 'Number of partners to retrieve (default: 50)',
                        'default': 50
                    }
                }
            }
        },
        {
            'name': 'odoo_create_partner',
            'description': 'Create a new business partner',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'name': {
                        'type': 'string',
                        'description': 'Partner name'
                    },
                    'email': {
                        'type': 'string',
                        'description': 'Email address'
                    },
                    'phone': {
                        'type': 'string',
                        'description': 'Phone number'
                    },
                    'street': {
                        'type': 'string',
                        'description': 'Street address'
                    },
                    'city': {
                        'type': 'string',
                        'description': 'City'
                    },
                    'zip_code': {
                        'type': 'string',
                        'description': 'ZIP code'
                    },
                    'vat': {
                        'type': 'string',
                        'description': 'VAT number'
                    }
                },
                'required': ['name']
            }
        },
        {
            'name': 'odoo_get_products',
            'description': 'Search products/services',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'search_term': {
                        'type': 'string',
                        'description': 'Search by name or code'
                    },
                    'limit': {
                        'type': 'integer',
                        'description': 'Number of products to retrieve (default: 50)',
                        'default': 50
                    }
                }
            }
        },
        {
            'name': 'odoo_get_financial_reports',
            'description': 'Get financial reports (P&L, Balance Sheet)',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'report_type': {
                        'type': 'string',
                        'description': 'Type of report',
                        'enum': ['profit_loss', 'balance_sheet'],
                        'default': 'balance_sheet'
                    },
                    'date_from': {
                        'type': 'string',
                        'description': 'Start date (YYYY-MM-DD)'
                    },
                    'date_to': {
                        'type': 'string',
                        'description': 'End date (YYYY-MM-DD)'
                    }
                }
            }
        },
        {
            'name': 'odoo_search_records',
            'description': 'Search records in any Odoo model',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'model': {
                        'type': 'string',
                        'description': 'Odoo model name (e.g., account.move, res.partner)'
                    },
                    'domain': {
                        'type': 'array',
                        'description': 'Search domain filters'
                    },
                    'limit': {
                        'type': 'integer',
                        'description': 'Number of records to retrieve',
                        'default': 50
                    },
                    'fields': {
                        'type': 'array',
                        'description': 'Fields to return',
                        'items': {'type': 'string'}
                    }
                },
                'required': ['model']
            }
        },
        {
            'name': 'odoo_read_record',
            'description': 'Read a specific record by ID',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'model': {
                        'type': 'string',
                        'description': 'Odoo model name'
                    },
                    'id': {
                        'type': 'integer',
                        'description': 'Record ID'
                    },
                    'fields': {
                        'type': 'array',
                        'description': 'Fields to return',
                        'items': {'type': 'string'}
                    }
                },
                'required': ['model', 'id']
            }
        },
        {
            'name': 'odoo_create_record',
            'description': 'Create a new record in any Odoo model',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'model': {
                        'type': 'string',
                        'description': 'Odoo model name'
                    },
                    'values': {
                        'type': 'object',
                        'description': 'Field values for the new record'
                    }
                },
                'required': ['model', 'values']
            }
        },
        {
            'name': 'odoo_write_record',
            'description': 'Update an existing record',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'model': {
                        'type': 'string',
                        'description': 'Odoo model name'
                    },
                    'id': {
                        'type': 'integer',
                        'description': 'Record ID to update'
                    },
                    'values': {
                        'type': 'object',
                        'description': 'Field values to update'
                    }
                },
                'required': ['model', 'id', 'values']
            }
        },
        {
            'name': 'odoo_unlink_record',
            'description': 'Delete a record',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'model': {
                        'type': 'string',
                        'description': 'Odoo model name'
                    },
                    'id': {
                        'type': 'integer',
                        'description': 'Record ID to delete'
                    }
                },
                'required': ['model', 'id']
            }
        }
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Execute an Odoo tool"""
    try:
        client = get_client()

        if name == 'odoo_connect':
            result = client.check_connection()
            return [{'type': 'text', 'text': json.dumps(result, indent=2, default=str)}]

        elif name == 'odoo_get_invoices':
            invoices = client.get_invoices(
                state=arguments.get('state'),
                limit=arguments.get('limit', 50),
                days=arguments.get('days'),
                partner_id=arguments.get('partner_id')
            )
            return [{'type': 'text', 'text': json.dumps(invoices, indent=2, default=str)}]

        elif name == 'odoo_create_invoice':
            invoice_id = client.create_invoice(
                partner_id=arguments['partner_id'],
                invoice_lines=arguments['invoice_lines'],
                invoice_date=arguments.get('invoice_date'),
                invoice_date_due=arguments.get('invoice_date_due'),
                move_type=arguments.get('move_type', 'out_invoice'),
                narrative=arguments.get('narrative')
            )
            return [{
                'type': 'text',
                'text': json.dumps({
                    'success': True,
                    'invoice_id': invoice_id,
                    'message': f'Invoice created with ID: {invoice_id}'
                }, indent=2)
            }]

        elif name == 'odoo_validate_invoice':
            client.validate_invoice(arguments['invoice_id'])
            return [{
                'type': 'text',
                'text': json.dumps({
                    'success': True,
                    'message': f'Invoice {arguments["invoice_id"]} validated successfully'
                }, indent=2)
            }]

        elif name == 'odoo_get_payments':
            payments = client.get_payments(
                state=arguments.get('state'),
                limit=arguments.get('limit', 50),
                days=arguments.get('days')
            )
            return [{'type': 'text', 'text': json.dumps(payments, indent=2, default=str)}]

        elif name == 'odoo_register_payment':
            payment_id = client.register_payment(
                invoice_id=arguments['invoice_id'],
                amount=arguments['amount'],
                payment_date=arguments.get('payment_date')
            )
            return [{
                'type': 'text',
                'text': json.dumps({
                    'success': True,
                    'payment_id': payment_id,
                    'message': f'Payment registered with ID: {payment_id}'
                }, indent=2)
            }]

        elif name == 'odoo_get_partners':
            partners = client.get_partners(
                search_term=arguments.get('search_term'),
                limit=arguments.get('limit', 50)
            )
            return [{'type': 'text', 'text': json.dumps(partners, indent=2, default=str)}]

        elif name == 'odoo_create_partner':
            partner_id = client.create_partner(
                name=arguments['name'],
                email=arguments.get('email'),
                phone=arguments.get('phone'),
                street=arguments.get('street'),
                city=arguments.get('city'),
                zip_code=arguments.get('zip_code'),
                vat=arguments.get('vat')
            )
            return [{
                'type': 'text',
                'text': json.dumps({
                    'success': True,
                    'partner_id': partner_id,
                    'message': f'Partner created with ID: {partner_id}'
                }, indent=2)
            }]

        elif name == 'odoo_get_products':
            products = client.get_products(
                search_term=arguments.get('search_term'),
                limit=arguments.get('limit', 50)
            )
            return [{'type': 'text', 'text': json.dumps(products, indent=2, default=str)}]

        elif name == 'odoo_get_financial_reports':
            report = client.get_financial_reports(
                report_type=arguments.get('report_type', 'balance_sheet'),
                date_from=arguments.get('date_from'),
                date_to=arguments.get('date_to')
            )
            return [{'type': 'text', 'text': json.dumps(report, indent=2, default=str)}]

        elif name == 'odoo_search_records':
            records = client.search(
                model=arguments['model'],
                domain=arguments.get('domain', []),
                limit=arguments.get('limit', 50),
                fields=arguments.get('fields')
            )
            return [{'type': 'text', 'text': json.dumps(records, indent=2, default=str)}]

        elif name == 'odoo_read_record':
            record = client.read(
                model=arguments['model'],
                id=arguments['id'],
                fields=arguments.get('fields')
            )
            return [{'type': 'text', 'text': json.dumps(record or {}, indent=2, default=str)}]

        elif name == 'odoo_create_record':
            record_id = client.create(
                model=arguments['model'],
                values=arguments['values']
            )
            return [{
                'type': 'text',
                'text': json.dumps({
                    'success': True,
                    'record_id': record_id,
                    'message': f'Record created with ID: {record_id}'
                }, indent=2)
            }]

        elif name == 'odoo_write_record':
            success = client.write(
                model=arguments['model'],
                id=arguments['id'],
                values=arguments['values']
            )
            return [{
                'type': 'text',
                'text': json.dumps({
                    'success': success,
                    'message': f'Record {arguments["id"]} updated successfully'
                }, indent=2)
            }]

        elif name == 'odoo_unlink_record':
            success = client.unlink(
                model=arguments['model'],
                id=arguments['id']
            )
            return [{
                'type': 'text',
                'text': json.dumps({
                    'success': success,
                    'message': f'Record {arguments["id"]} deleted successfully'
                }, indent=2)
            }]

        else:
            return [{'type': 'text', 'text': f'Unknown tool: {name}'}]

    except Exception as e:
        logger.error(f'Tool execution error: {str(e)}')
        return [{'type': 'text', 'text': f'Error: {str(e)}'}]


async def main():
    """Run the Odoo MCP server"""
    logger.info('Starting Odoo MCP Server...')

    # Verify configuration
    if not all([ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD]):
        logger.warning('Odoo credentials not fully configured')
    else:
        logger.info(f'Odoo URL: {ODOO_URL}')
        logger.info(f'Odoo Database: {ODOO_DB}')
        logger.info(f'Odoo Username: {ODOO_USERNAME}')

    async with mcp.server.stdio.stdio_server() as (read, write):
        await server.run(read, write)


if __name__ == '__main__':
    asyncio.run(main())

#!/usr/bin/env python3

"""
Parses introspection query response JSON
"""

from graphql import build_client_schema, GraphQLScalarType, is_specified_scalar_type, parse, Visitor, ValidationContext, visit
from graphql.language.ast import VariableDefinitionNode, NonNullTypeNode, NamedTypeNode
import json

def get_custom_scalars(introspection_resp):
    schema = build_client_schema(introspection_resp["data"])

    custom_scalars = [
        type_name for type_name, type_obj in schema.type_map.items()
        if isinstance(type_obj, GraphQLScalarType) and not is_specified_scalar_type(type_obj)
    ]

    return custom_scalars


def get_required_vars(introspection_resp, graphql_payload):
    schema = build_client_schema(introspection_resp["data"])
    query_string = graphql_payload.get('query', '')

    try:
        ast = parse(query_string)
    except Exception as e:
        raise ValueError(f"Invalid GraphQL query string: {e}")

    required_vars = {}

    def get_type_name(type_node):
        if isinstance(type_node, NonNullTypeNode):
            return get_type_name(type_node.type)
        if isinstance(type_node, NamedTypeNode):
            return type_node.name.value
        return str(type_node)

    class VariableVisitor(Visitor):
        def enter_variable_definition(self, node: VariableDefinitionNode, *args, **kwargs):
            if isinstance(node.type, NonNullTypeNode):
                var_name = node.variable.name.value
                var_type = get_type_name(node.type)

                if node.default_value is None:
                    required_vars[var_name] = f"{var_type}!"

    visit(ast, VariableVisitor())

    return required_vars

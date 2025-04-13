"""
Command-line interface commands for ChromaLens.

This module defines the commands available in the CLI.
"""

import json
import sys
import os
from typing import Optional, List, Dict, Any, Tuple

import click
from tabulate import tabulate

from chromalens.client.client import ChromaLensClient
from chromalens.utils.formatters import (
    format_json,
    format_collection_info,
    format_query_results,
    format_table,
)
from chromalens.utils.embedding_functions import text_to_embeddings


# Shared CLI options
def common_options(func):
    """Add common options to a CLI command."""
    options = [
        click.option('--host', '-h', help='ChromaDB server host', default='localhost'),
        click.option('--port', '-p', type=int, help='ChromaDB server port', default=8000),
        click.option('--tenant', '-t', help='Tenant name', default='default_tenant'),
        click.option('--database', '-d', help='Database name', default='default_database'),
        click.option('--ssl/--no-ssl', help='Use HTTPS', default=False),
        click.option('--api-key', help='API key for authentication'),
        click.option('--json', is_flag=True, help='Output in JSON format'),
        click.option('--verbose', '-v', is_flag=True, help='Enable verbose output'),
    ]
    
    for option in reversed(options):
        func = option(func)
    
    return func


def get_client(host, port, tenant, database, ssl, api_key, verbose):
    """Get a ChromaLensClient instance with the specified options."""
    if verbose:
        click.echo(f"Connecting to ChromaDB at {host}:{port}")
    
    return ChromaLensClient(
        host=host,
        port=port,
        tenant=tenant,
        database=database,
        ssl=ssl,
        api_key=api_key,
    )


@click.group()
@click.version_option()
def cli():
    """ChromaLens CLI - A command-line interface for ChromaDB."""
    pass


# ========== System Commands ==========

@cli.command(name='heartbeat')
@common_options
def heartbeat_command(host, port, tenant, database, ssl, api_key, json, verbose):
    """Check server heartbeat to verify connectivity."""
    try:
        client = get_client(host, port, tenant, database, ssl, api_key, verbose)
        response = client.heartbeat()
        
        if json:
            click.echo(format_json(response))
        else:
            click.echo(f"Server is running! Heartbeat: {response}")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command(name='version')
@common_options
def version_command(host, port, tenant, database, ssl, api_key, json, verbose):
    """Get server version information."""
    try:
        client = get_client(host, port, tenant, database, ssl, api_key, verbose)
        response = client.version()
        
        if json:
            click.echo(format_json(response))
        else:
            click.echo(f"Server version: {response}")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command(name='reset')
@common_options
@click.option('--confirm', is_flag=True, help='Confirm deletion of all data')
def reset_command(host, port, tenant, database, ssl, api_key, json, verbose, confirm):
    """Reset the ChromaDB server (warning: destructive operation)."""
    if not confirm:
        click.echo("Warning: This will delete all data in the server.")
        click.echo("To confirm, run with --confirm")
        sys.exit(1)
    
    try:
        client = get_client(host, port, tenant, database, ssl, api_key, verbose)
        response = client.reset()
        
        if json:
            click.echo(format_json(response))
        else:
            click.echo("Server reset successfully.")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# ========== Tenant Commands ==========

@cli.command(name='tenant-list')
@common_options
def tenant_list_command(host, port, tenant, database, ssl, api_key, json, verbose):
    """List all tenants."""
    try:
        client = get_client(host, port, tenant, database, ssl, api_key, verbose)
        response = client.list_tenants()
        
        if json:
            click.echo(format_json(response))
        else:
            if not response:
                click.echo("No tenants found.")
                return
            
            table = []
            for t in response:
                table.append([t.get('id', 'Unknown'), t.get('name', 'Unknown')])
            
            click.echo(tabulate(table, headers=['ID', 'Name'], tablefmt='simple'))
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command(name='tenant-create')
@common_options
@click.argument('name')
def tenant_create_command(host, port, tenant, database, ssl, api_key, json, verbose, name):
    """Create a new tenant."""
    try:
        client = get_client(host, port, tenant, database, ssl, api_key, verbose)
        response = client.create_tenant(name)
        
        if json:
            click.echo(format_json(response))
        else:
            click.echo(f"Tenant '{name}' created successfully.")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command(name='tenant-get')
@common_options
@click.argument('name')
def tenant_get_command(host, port, tenant, database, ssl, api_key, json, verbose, name):
    """Get information about a tenant."""
    try:
        client = get_client(host, port, tenant, database, ssl, api_key, verbose)
        response = client.get_tenant(name)
        
        if json:
            click.echo(format_json(response))
        else:
            click.echo(f"Tenant: {response.get('name', 'Unknown')}")
            click.echo(f"ID: {response.get('id', 'Unknown')}")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# ========== Database Commands ==========

@cli.command(name='db-list')
@common_options
def database_list_command(host, port, tenant, database, ssl, api_key, json, verbose):
    """List all databases for a tenant."""
    try:
        client = get_client(host, port, tenant, database, ssl, api_key, verbose)
        response = client.list_databases(tenant=tenant)
        
        if json:
            click.echo(format_json(response))
        else:
            if not response:
                click.echo(f"No databases found for tenant '{tenant}'.")
                return
            
            table = []
            for db in response:
                table.append([
                    db.get('id', 'Unknown'),
                    db.get('name', 'Unknown'),
                    db.get('tenant', 'Unknown')
                ])
            
            click.echo(tabulate(table, headers=['ID', 'Name', 'Tenant'], tablefmt='simple'))
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command(name='db-create')
@common_options
@click.argument('name')
def database_create_command(host, port, tenant, database, ssl, api_key, json, verbose, name):
    """Create a new database."""
    try:
        client = get_client(host, port, tenant, database, ssl, api_key, verbose)
        response = client.create_database(name, tenant=tenant)
        
        if json:
            click.echo(format_json(response))
        else:
            click.echo(f"Database '{name}' created successfully in tenant '{tenant}'.")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command(name='db-get')
@common_options
@click.argument('name')
def database_get_command(host, port, tenant, database, ssl, api_key, json, verbose, name):
    """Get information about a database."""
    try:
        client = get_client(host, port, tenant, database, ssl, api_key, verbose)
        response = client.get_database(name, tenant=tenant)
        
        if json:
            click.echo(format_json(response))
        else:
            click.echo(f"Database: {response.get('name', 'Unknown')}")
            click.echo(f"ID: {response.get('id', 'Unknown')}")
            click.echo(f"Tenant: {response.get('tenant', 'Unknown')}")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command(name='db-delete')
@common_options
@click.argument('name')
@click.option('--confirm', is_flag=True, help='Confirm deletion')
def database_delete_command(host, port, tenant, database, ssl, api_key, json, verbose, name, confirm):
    """Delete a database."""
    if not confirm:
        click.echo(f"Warning: This will delete database '{name}' and all its collections.")
        click.echo("To confirm, run with --confirm")
        sys.exit(1)
    
    try:
        client = get_client(host, port, tenant, database, ssl, api_key, verbose)
        response = client.delete_database(name, tenant=tenant)
        
        if json:
            click.echo(format_json(response))
        else:
            click.echo(f"Database '{name}' deleted successfully from tenant '{tenant}'.")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# ========== Collection Commands ==========

@cli.command(name='coll-list')
@common_options
def collection_list_command(host, port, tenant, database, ssl, api_key, json, verbose):
    """List all collections in a database."""
    try:
        client = get_client(host, port, tenant, database, ssl, api_key, verbose)
        response = client.list_collections(database=database, tenant=tenant)
        
        if json:
            click.echo(format_json(response))
        else:
            if not response:
                click.echo(f"No collections found in database '{database}'.")
                return
            
            table = []
            for coll in response:
                table.append([
                    coll.get('id', 'Unknown')[:8] + '...',
                    coll.get('name', 'Unknown'),
                    coll.get('dimension', 'Unknown'),
                    'Yes' if coll.get('metadata') else 'No'
                ])
            
            click.echo(tabulate(table, headers=['ID', 'Name', 'Dimension', 'Has Metadata'], tablefmt='simple'))
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command(name='coll-create')
@common_options
@click.argument('name')
@click.option('--dimension', type=int, help='Vector dimension', default=768)
@click.option('--metadata', help='JSON metadata')
def collection_create_command(host, port, tenant, database, ssl, api_key, json, verbose, name, dimension, metadata):
    """Create a new collection."""
    # Parse metadata if provided
    metadata_dict = None
    if metadata:
        try:
            metadata_dict = json.loads(metadata)
        except json.JSONDecodeError:
            click.echo("Error: Invalid JSON in metadata", err=True)
            sys.exit(1)
    
    try:
        client = get_client(host, port, tenant, database, ssl, api_key, verbose)
        response = client.create_collection(
            name=name,
            metadata=metadata_dict,
            dimension=dimension,
            database=database,
            tenant=tenant
        )
        
        if json:
            click.echo(format_json(response))
        else:
            click.echo(f"Collection '{name}' created successfully.")
            click.echo(f"Dimension: {dimension}")
            if metadata_dict:
                click.echo(f"Metadata: {metadata_dict}")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command(name='coll-get')
@common_options
@click.argument('name')
def collection_get_command(host, port, tenant, database, ssl, api_key, json, verbose, name):
    """Get information about a collection."""
    try:
        client = get_client(host, port, tenant, database, ssl, api_key, verbose)
        response = client.get_collection(name, database=database, tenant=tenant)
        
        if json:
            click.echo(format_json(response))
        else:
            click.echo(format_collection_info(response))
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command(name='coll-delete')
@common_options
@click.argument('name')
@click.option('--confirm', is_flag=True, help='Confirm deletion')
def collection_delete_command(host, port, tenant, database, ssl, api_key, json, verbose, name, confirm):
    """Delete a collection."""
    if not confirm:
        click.echo(f"Warning: This will delete collection '{name}' and all its data.")
        click.echo("To confirm, run with --confirm")
        sys.exit(1)
    
    try:
        client = get_client(host, port, tenant, database, ssl, api_key, verbose)
        response = client.delete_collection(name, database=database, tenant=tenant)
        
        if json:
            click.echo(format_json(response))
        else:
            click.echo(f"Collection '{name}' deleted successfully.")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command(name='coll-count')
@common_options
@click.argument('collection_id')
def collection_count_command(host, port, tenant, database, ssl, api_key, json, verbose, collection_id):
    """Count items in a collection."""
    try:
        client = get_client(host, port, tenant, database, ssl, api_key, verbose)
        response = client.count_items(collection_id, database=database, tenant=tenant)
        
        if json:
            click.echo(format_json({"count": response}))
        else:
            click.echo(f"Collection has {response} items.")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# ========== Collection Data Commands ==========

@cli.command(name='data-add')
@common_options
@click.argument('collection_id')
@click.option('--ids', help='Comma-separated list of IDs')
@click.option('--texts', help='Comma-separated list of texts to embed')
@click.option('--embeddings-file', help='JSON file containing embeddings')
@click.option('--metadatas-file', help='JSON file containing metadatas')
@click.option('--documents-file', help='Text file containing documents, one per line')
@click.option('--embedding-provider', help='Embedding provider (openai, huggingface, etc.)', default='default')
@click.option('--api-key-embedding', help='API key for embedding provider')
def data_add_command(
    host, port, tenant, database, ssl, api_key, json, verbose,
    collection_id, ids, texts, embeddings_file, metadatas_file, documents_file,
    embedding_provider, api_key_embedding
):
    """Add items to a collection."""
    # Parse IDs if provided
    id_list = None
    if ids:
        id_list = [id.strip() for id in ids.split(',')]
    
    # Parse texts if provided
    text_list = None
    if texts:
        text_list = [text.strip() for text in texts.split(',')]
    
    # Load documents from file if provided
    document_list = None
    if documents_file:
        try:
            with open(documents_file, 'r') as f:
                document_list = [line.strip() for line in f if line.strip()]
        except Exception as e:
            click.echo(f"Error loading documents file: {e}", err=True)
            sys.exit(1)
    
    # Load embeddings from file if provided
    embedding_list = None
    if embeddings_file:
        try:
            with open(embeddings_file, 'r') as f:
                embedding_list = json.load(f)
        except Exception as e:
            click.echo(f"Error loading embeddings file: {e}", err=True)
            sys.exit(1)
    
    # Load metadatas from file if provided
    metadata_list = None
    if metadatas_file:
        try:
            with open(metadatas_file, 'r') as f:
                metadata_list = json.load(f)
        except Exception as e:
            click.echo(f"Error loading metadatas file: {e}", err=True)
            sys.exit(1)
    
    # Generate embeddings from texts if needed
    if (text_list or document_list) and not embedding_list:
        texts_to_embed = text_list or document_list
        try:
            embedding_list = text_to_embeddings(
                texts=texts_to_embed,
                provider=embedding_provider,
                api_key=api_key_embedding
            )
        except Exception as e:
            click.echo(f"Error generating embeddings: {e}", err=True)
            sys.exit(1)
    
    # Validate we have embeddings
    if not embedding_list:
        click.echo("Error: No embeddings provided. Use --texts, --documents-file, or --embeddings-file.", err=True)
        sys.exit(1)
    
    try:
        client = get_client(host, port, tenant, database, ssl, api_key, verbose)
        response = client.add(
            collection_id=collection_id,
            embeddings=embedding_list,
            metadatas=metadata_list,
            documents=document_list or text_list,
            ids=id_list,
            database=database,
            tenant=tenant
        )
        
        if json:
            click.echo(format_json(response))
        else:
            click.echo(f"Added {len(embedding_list)} items to collection.")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command(name='data-get')
@common_options
@click.argument('collection_id')
@click.option('--ids', help='Comma-separated list of IDs to retrieve')
@click.option('--where', help='JSON where filter')
@click.option('--limit', type=int, help='Maximum number of results', default=10)
@click.option('--include-embeddings', is_flag=True, help='Include embeddings in the response')
def data_get_command(
    host, port, tenant, database, ssl, api_key, json, verbose,
    collection_id, ids, where, limit, include_embeddings
):
    """Get items from a collection."""
    # Parse IDs if provided
    id_list = None
    if ids:
        id_list = [id.strip() for id in ids.split(',')]
    
    # Parse where filter if provided
    where_filter = None
    if where:
        try:
            where_filter = json.loads(where)
        except json.JSONDecodeError:
            click.echo("Error: Invalid JSON in where filter", err=True)
            sys.exit(1)
    
    # Determine fields to include
    include = ["metadatas", "documents"]
    if include_embeddings:
        include.append("embeddings")
    
    try:
        client = get_client(host, port, tenant, database, ssl, api_key, verbose)
        response = client.get(
            collection_id=collection_id,
            ids=id_list,
            where=where_filter,
            limit=limit,
            include=include,
            database=database,
            tenant=tenant
        )
        
        if json:
            click.echo(format_json(response))
        else:
            if not response.get('ids'):
                click.echo("No items found.")
                return
            
            click.echo(f"Found {len(response.get('ids', []))} items:")
            
            # Display items
            table = []
            for i, item_id in enumerate(response.get('ids', [])):
                row = [item_id]
                
                # Add metadata if available
                if response.get('metadatas'):
                    metadata = response['metadatas'][i]
                    row.append(str(metadata) if metadata else "None")
                else:
                    row.append("N/A")
                
                # Add document if available
                if response.get('documents'):
                    document = response['documents'][i]
                    if document and len(document) > 50:
                        row.append(document[:50] + "...")
                    else:
                        row.append(document or "None")
                else:
                    row.append("N/A")
                
                table.append(row)
            
            headers = ['ID', 'Metadata', 'Document']
            click.echo(tabulate(table, headers=headers, tablefmt='simple'))
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command(name='data-delete')
@common_options
@click.argument('collection_id')
@click.option('--ids', help='Comma-separated list of IDs to delete')
@click.option('--where', help='JSON where filter')
@click.option('--confirm', is_flag=True, help='Confirm deletion')
def data_delete_command(
    host, port, tenant, database, ssl, api_key, json, verbose,
    collection_id, ids, where, confirm
):
    """Delete items from a collection."""
    # Parse IDs if provided
    id_list = None
    if ids:
        id_list = [id.strip() for id in ids.split(',')]
    
    # Parse where filter if provided
    where_filter = None
    if where:
        try:
            where_filter = json.loads(where)
        except json.JSONDecodeError:
            click.echo("Error: Invalid JSON in where filter", err=True)
            sys.exit(1)
    
    # Check if we have a filter
    if not id_list and not where_filter:
        click.echo("Error: Either --ids or --where must be provided.", err=True)
        sys.exit(1)
    
    if not confirm:
        click.echo("Warning: This will delete items from the collection.")
        click.echo("To confirm, run with --confirm")
        sys.exit(1)
    
    try:
        client = get_client(host, port, tenant, database, ssl, api_key, verbose)
        response = client.delete(
            collection_id=collection_id,
            ids=id_list,
            where=where_filter,
            database=database,
            tenant=tenant
        )
        
        if json:
            click.echo(format_json(response))
        else:
            click.echo("Items deleted successfully.")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command(name='data-query')
@common_options
@click.argument('collection_id')
@click.option('--text', help='Text to convert to embedding and query')
@click.option('--embedding-file', help='JSON file containing embedding to query')
@click.option('--where', help='JSON where filter')
@click.option('--n-results', type=int, help='Number of results to return', default=10)
@click.option('--embedding-provider', help='Embedding provider (openai, huggingface, etc.)', default='default')
@click.option('--api-key-embedding', help='API key for embedding provider')
@click.option('--include-embeddings', is_flag=True, help='Include embeddings in the response')
def data_query_command(
    host, port, tenant, database, ssl, api_key, json, verbose,
    collection_id, text, embedding_file, where, n_results, 
    embedding_provider, api_key_embedding, include_embeddings
):
    """Query a collection for nearest neighbors."""
    # Get the embedding
    query_embedding = None
    
    if text:
        # Generate embedding from text
        try:
            embeddings = text_to_embeddings(
                texts=[text],
                provider=embedding_provider,
                api_key=api_key_embedding
            )
            query_embedding = embeddings[0]
        except Exception as e:
            click.echo(f"Error generating embedding: {e}", err=True)
            sys.exit(1)
    
    elif embedding_file:
        # Load embedding from file
        try:
            with open(embedding_file, 'r') as f:
                query_embedding = json.load(f)
        except Exception as e:
            click.echo(f"Error loading embedding file: {e}", err=True)
            sys.exit(1)
    
    else:
        click.echo("Error: Either --text or --embedding-file must be provided.", err=True)
        sys.exit(1)
    
    # Parse where filter if provided
    where_filter = None
    if where:
        try:
            where_filter = json.loads(where)
        except json.JSONDecodeError:
            click.echo("Error: Invalid JSON in where filter", err=True)
            sys.exit(1)
    
    # Determine fields to include
    include = ["metadatas", "documents", "distances"]
    if include_embeddings:
        include.append("embeddings")
    
    try:
        client = get_client(host, port, tenant, database, ssl, api_key, verbose)
        response = client.query(
            collection_id=collection_id,
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_filter,
            include=include,
            database=database,
            tenant=tenant
        )
        
        if json:
            click.echo(format_json(response))
        else:
            click.echo(format_query_results(response))
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
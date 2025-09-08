#!/usr/bin/env python3
"""
Firestore Cleanup Script

This script helps you clear all chat sessions and custom entities from Firestore collections.
Use with caution as this will permanently delete all session and entity data.

Usage:
    python clear_firestore_sessions.py [--project-id PROJECT_ID] [--confirm] [--collections COLLECTIONS]
    
Options:
    --project-id    Google Cloud project ID (default: firestore-470903)
    --confirm       Skip confirmation prompt (use with caution)
    --dry-run       Show what would be deleted without actually deleting
    --collections   Comma-separated list of collections to clean (default: chat_sessions,custom_entities)
"""

import argparse
import sys
from typing import Optional
import logging

from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clear_firestore_collections(project_id: str, collections: list, dry_run: bool = False, confirm: bool = False):
    """
    Clear all documents from specified Firestore collections
    
    Args:
        project_id: Google Cloud project ID
        collections: List of collection names to clean
        dry_run: If True, only show what would be deleted
        confirm: If True, skip confirmation prompt
    """
    try:
        # Import Firestore client
        from google.cloud import firestore
        
        logger.info(f"🔗 Connecting to Firestore project: {project_id}")
        db = firestore.Client(project=project_id)
        
        # Process each collection
        total_docs_all_collections = 0
        collection_stats = {}
        
        for collection_name in collections:
            logger.info(f"📋 Processing collection: {collection_name}")
            collection_ref = db.collection(collection_name)
            
            # Get all documents in the collection
            docs = collection_ref.stream()
            doc_list = list(docs)
            total_docs = len(doc_list)
            
            collection_stats[collection_name] = {
                'count': total_docs,
                'docs': doc_list
            }
            total_docs_all_collections += total_docs
            
            if total_docs == 0:
                logger.info(f"✅ No documents found in {collection_name} collection")
            else:
                logger.info(f"📊 Found {total_docs} documents in {collection_name}")
        
        if total_docs_all_collections == 0:
            logger.info("✅ No documents found in any collection. Nothing to delete.")
            return
        
        # Show dry run details
        if dry_run:
            logger.info("🔍 DRY RUN - Documents that would be deleted:")
            for collection_name, stats in collection_stats.items():
                if stats['count'] > 0:
                    logger.info(f"\n📁 Collection: {collection_name} ({stats['count']} documents)")
                    for i, doc in enumerate(stats['docs'][:5], 1):  # Show first 5 docs
                        doc_data = doc.to_dict()
                        doc_id = doc.id
                        
                        if collection_name == 'chat_sessions':
                            last_updated = doc_data.get('last_updated', 'Unknown')
                            messages_count = len(doc_data.get('messages', []))
                            entities_count = len(doc_data.get('extracted_entities', []))
                            logger.info(f"  {i}. Session ID: {doc_id}")
                            logger.info(f"     Last Updated: {last_updated}")
                            logger.info(f"     Messages: {messages_count}, Entities: {entities_count}")
                        elif collection_name == 'custom_entities':
                            entity_name = doc_data.get('entity_name', 'Unknown')
                            entity_type = doc_data.get('entity_type', 'Unknown')
                            session_id = doc_data.get('session_id', 'Unknown')
                            logger.info(f"  {i}. Entity ID: {doc_id}")
                            logger.info(f"     Name: {entity_name}, Type: {entity_type}")
                            logger.info(f"     Session: {session_id}")
                    
                    if stats['count'] > 5:
                        logger.info(f"     ... and {stats['count'] - 5} more documents")
            
            logger.info(f"\n🔍 DRY RUN - Would delete {total_docs_all_collections} documents total")
            return
        
        # Confirmation prompt
        if not confirm:
            print(f"\n⚠️  WARNING: This will permanently delete {total_docs_all_collections} documents!")
            print("Collections to be cleaned:")
            for collection_name, stats in collection_stats.items():
                if stats['count'] > 0:
                    print(f"  - {collection_name}: {stats['count']} documents")
            print("\nThis action cannot be undone.")
            response = input("\nAre you sure you want to continue? (yes/no): ").lower().strip()
            
            if response not in ['yes', 'y']:
                logger.info("❌ Operation cancelled by user")
                return
        
        # Delete all documents from all collections
        total_deleted = 0
        
        for collection_name, stats in collection_stats.items():
            if stats['count'] == 0:
                continue
                
            logger.info(f"🗑️  Deleting {stats['count']} documents from {collection_name}...")
            
            # Use batch delete for efficiency
            batch = db.batch()
            batch_count = 0
            deleted_count = 0
            
            for doc in stats['docs']:
                batch.delete(doc.reference)
                batch_count += 1
                deleted_count += 1
                
                # Firestore batch limit is 500 operations
                if batch_count >= 500:
                    batch.commit()
                    logger.info(f"✅ Deleted batch of {batch_count} documents from {collection_name}")
                    batch = db.batch()
                    batch_count = 0
            
            # Commit remaining batch
            if batch_count > 0:
                batch.commit()
                logger.info(f"✅ Deleted final batch of {batch_count} documents from {collection_name}")
            
            logger.info(f"🎉 Successfully deleted {deleted_count} documents from {collection_name}!")
            total_deleted += deleted_count
        
        logger.info(f"🎉 Successfully deleted {total_deleted} documents from {len(collections)} collections!")
        logger.info("✅ All specified Firestore collections are now empty")
        
    except ImportError:
        logger.error("❌ Error: google-cloud-firestore package not found")
        logger.error("Please install it with: pip install google-cloud-firestore")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error clearing Firestore sessions: {str(e)}")
        sys.exit(1)

def main():
    """Main function to handle command line arguments"""
    parser = argparse.ArgumentParser(
        description="Clear all documents from specified Firestore collections",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Dry run to see what would be deleted (both collections)
    python clear_firestore_sessions.py --dry-run
    
    # Clear both collections with confirmation prompt
    python clear_firestore_sessions.py
    
    # Clear only chat_sessions collection
    python clear_firestore_sessions.py --collections chat_sessions
    
    # Clear only custom_entities collection
    python clear_firestore_sessions.py --collections custom_entities
    
    # Clear without confirmation (use with caution)
    python clear_firestore_sessions.py --confirm
    
    # Use different project ID
    python clear_firestore_sessions.py --project-id my-project-id
        """
    )
    
    parser.add_argument(
        '--project-id',
        default=Config.get_project_id(),
        help=f'Google Cloud project ID (default: {Config.get_project_id()})'
    )
    
    parser.add_argument(
        '--confirm',
        action='store_true',
        help='Skip confirmation prompt (use with caution)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be deleted without actually deleting'
    )
    
    parser.add_argument(
        '--collections',
        default=f'{Config.FIRESTORE_COLLECTION_CHAT_SESSIONS},{Config.FIRESTORE_COLLECTION_CUSTOM_ENTITIES}',
        help=f'Comma-separated list of collections to clean (default: {Config.FIRESTORE_COLLECTION_CHAT_SESSIONS},{Config.FIRESTORE_COLLECTION_CUSTOM_ENTITIES})'
    )
    
    args = parser.parse_args()
    
    # Parse collections
    collections = [col.strip() for col in args.collections.split(',') if col.strip()]
    
    # Print header
    print("🧹 Firestore Cleanup Tool")
    print("=" * 50)
    print(f"Project ID: {args.project_id}")
    print(f"Collections: {', '.join(collections)}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'DELETE'}")
    print("=" * 50)
    
    # Run the cleanup
    clear_firestore_collections(
        project_id=args.project_id,
        collections=collections,
        dry_run=args.dry_run,
        confirm=args.confirm
    )

if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""
Document processor for Extendicare quiz bot.
This module handles the conversion of policy documents to a format suitable for the chatbot.
"""
import os
import re
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def process_policy_documents(root_directory=None):
    """
    Process all policy documents in the specified directory structure.
    
    Expected structure:
    root_directory/
        policy_manual_1/
            Policy/
                01_Policy_Name.docx
            Procedures/
                01_Procedure_Name.pptx
            Tools/
                01_Tool_Name.pdf
            Education/
                01_Education_Resource.pptx
        policy_manual_2/
            ...
    
    Parameters:
    -----------
    root_directory : str, optional
        Path to the directory containing policy documents. 
        If None, uses RAW_DOCUMENTS_PATH from environment.
    
    Returns:
    --------
    pandas.DataFrame
        Metadata for all processed documents
    """
    # Use environment variable if no directory specified
    if root_directory is None:
        root_directory = os.getenv('RAW_DOCUMENTS_PATH', './data/raw')
    
    print(f"Processing documents from: {root_directory}")
    
    documents = []
    
    # Get all direct subdirectories (policy manuals)
    policy_manuals = [d for d in os.listdir(root_directory) 
                     if os.path.isdir(os.path.join(root_directory, d))]
    
    print(f"Found {len(policy_manuals)} potential policy manuals")
    
    # Process each policy manual
    for policy_manual in policy_manuals:
        manual_path = os.path.join(root_directory, policy_manual)
        
        # Check for required subfolders
        resource_types = [d for d in os.listdir(manual_path) 
                         if os.path.isdir(os.path.join(manual_path, d)) 
                         and d in ['Policy', 'Procedures', 'Tools', 'Education']]
        
        # Skip if this directory doesn't have any of our expected resource type folders
        if not resource_types:
            print(f"Skipping {policy_manual} - no valid resource type folders found")
            continue
        
        print(f"Processing {policy_manual} with resource types: {resource_types}")
        
        # Process each resource type folder
        for resource_type in resource_types:
            type_path = os.path.join(manual_path, resource_type)
            
            # Process files in this folder
            for filename in os.listdir(type_path):
                file_path = os.path.join(type_path, filename)
                
                # Skip if not a file
                if not os.path.isfile(file_path):
                    continue
                
                # Extract index from filename (assuming format: "01_Name.ext")
                index_match = re.match(r'(\d+)_(.*)\.(.*)', filename)
                if index_match:
                    index = index_match.group(1)
                    name = index_match.group(2).replace('_', ' ')
                    extension = index_match.group(3).lower()
                else:
                    # Handle files without proper naming
                    index = "0"
                    name = os.path.splitext(filename)[0]
                    extension = os.path.splitext(filename)[1][1:].lower()
                
                # Create document metadata
                doc_info = {
                    'policy_manual': policy_manual,
                    'resource_type': resource_type,
                    'index': index,
                    'name': name,
                    'filename': filename,
                    'file_path': file_path,
                    'extension': extension
                }
                
                documents.append(doc_info)
                print(f"  Added: {policy_manual}/{resource_type}/{filename}")
    
    # Create DataFrame from collected data
    df = pd.DataFrame(documents) if documents else pd.DataFrame({
        'policy_manual': [],
        'resource_type': [],
        'index': [],
        'name': [],
        'filename': [],
        'file_path': [],
        'extension': []
    })
    
    return df

def main():
    """Main function to run the document processor."""
    print("Starting document processing...")
    df = process_policy_documents()
    print(f"Processed {len(df)} documents")
    
    if not df.empty:
        print("\nSummary by policy manual:")
        print(df['policy_manual'].value_counts())
        
        print("\nSummary by resource type:")
        print(df['resource_type'].value_counts())
    else:
        print("No documents were processed.")
    
    # Save metadata
    output_path = os.getenv('PROCESSED_DOCUMENTS_PATH', './data/processed')
    os.makedirs(output_path, exist_ok=True)
    metadata_path = os.path.join(output_path, 'document_metadata.csv')
    print(f"Saving metadata to: {metadata_path}")
    
    if not df.empty:
        df.to_csv(metadata_path, index=False)
        print(f"Saved metadata for {len(df)} documents")
    else:
        print("No metadata to save")
    
    print("Document processing complete!")

if __name__ == "__main__":
    main()

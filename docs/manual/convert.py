from openai import OpenAI
import os

# Set your OpenAI API key
client = OpenAI(api_key='your open ai key :)')

def rst_to_markdown(rst_file_path, md_file_path):
    """
    Convert a .rst file to Markdown using OpenAI GPT model.
    """
    # Open and read the .rst file
    with open(rst_file_path, 'r') as rst_file:
        rst_content = rst_file.read()
    
    print(f"Converting {rst_file_path} to Markdown...")
    messages = [
        {"role": "system", "content": "You are reStructuredText(rst) to markdown converter, User will send You rst and You will convert it to markdown only, keep the hierarchy and content same,and also if there is any refrense to rst file in rstfiles chagne the refrence to md file without changing the file name it to markdown file and just convert rst type ro md type."},
        {"role": "user", "content": f"{rst_content}"}
    ]
    # Send the content to OpenAI for conversion
    response = client.chat.completions.create(model="gpt-4o",
        messages=messages)
    
    # Get the Markdown content from the response
    md_content = response.choices[0].message.content.strip()

    # Write the Markdown content to the specified .md file
    with open(md_file_path, 'w') as md_file:
        md_file.write(md_content)
    
    print(f"Markdown file saved at: {md_file_path}")

def convert_all_rst_in_folder(folder_path):
    """
    Recursively find all .rst files in the specified folder, convert each to Markdown, and delete the original .rst file.
    """
    # Traverse through the folder and subfolders
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.rst'):
                rst_file_path = os.path.join(root, file)
                # Define the output .md file path (in the same directory)
                md_file_path = os.path.join(root, file.replace('.rst', '.md'))
                
                # Convert the rst file to markdown
                rst_to_markdown(rst_file_path, md_file_path)
                
                # Remove the original .rst file after conversion
                os.remove(rst_file_path)
                print(f"Removed original file: {rst_file_path}")

# Specify the root folder containing .rst files
folder_path = '.'

# Convert all .rst files in the folder and subfolders to Markdown, and remove original .rst files
convert_all_rst_in_folder(folder_path)

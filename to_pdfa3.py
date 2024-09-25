import pikepdf
import hashlib
import subprocess
import os
import multiprocessing

from pathlib import Path

def embed_fonts_with_ghostscript_multi(input_pdfs, output_dir, threads=8):
    """
    Use Ghostscript to embed all fonts and ensure PDF/A-3 compliance.
    """
    gs_command = [
        "gs", "-dBATCH", "-dNOPAUSE", "-sDEVICE=pdfwrite",
        "-dPDFSETTINGS=/prepress", "-dEmbedAllFonts=true",
        "-dSubsetFonts=true", "-dAutoRotatePages=/None",
        "-dCompatibilityLevel=1.4", "-dPDFA=2", "-dPDFACompatibilityPolicy=1",
        "-sOutputFile=" + output_dir + "/intermediate_%d.pdf"
    ]
    gs_command.extend(input_pdfs)

    try:
        subprocess.run(gs_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"Ghostscript command failed: {e}")
        print(f"Ghostscript stdout: {e.stdout.decode()}")
        print(f"Ghostscript stderr: {e.stderr.decode()}")
        raise

def embed_fonts_with_ghostscript(input_pdf, output_pdf, threads=8):
    """
    Use Ghostscript to embed all fonts and ensure PDF/A-3 compliance.
    """
    gs_command = [
        "gs",
        "-q",  # Add this line to suppress Ghostscript's informational output
        "-dPDFA=3",
        "-dBATCH",
        "-dNOPAUSE",
        "-sDEVICE=pdfwrite",
        "-dEmbedAllFonts=true",
        "-dPDFSETTINGS=/prepress",
        f"-dNumRenderingThreads={threads}",
        f"-sOutputFile={output_pdf}",
        input_pdf
    ]

    try:
        subprocess.run(gs_command, check=True, stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print(f"Error embedding fonts: {e}")

def embed_icc_profile_and_fix_trailer(input_pdf_path, icc_profile_path, final_output_pdf):
    """
    Embed the ICC profile and fix the trailer by adding the ID to ensure PDF/A compliance.
    """
    # Step 1: Open the PDF using pikepdf
    with pikepdf.open(input_pdf_path) as pdf:
        # Step 2: Embed the ICC profile
        with open(icc_profile_path, 'rb') as icc_file:
            icc_profile_data = icc_file.read()

        # Add the ICC profile as a new stream in the PDF
        icc_stream = pdf.make_stream(icc_profile_data)
        icc_stream.Type = pikepdf.Name("/OutputIntent")
        icc_stream.Subtype = pikepdf.Name("/GTS_PDFA1")
        icc_stream["/S"] = pikepdf.Name("/GTS_PDFA1")
        icc_stream["/OutputConditionIdentifier"] = "sRGB ICC Profile"
        icc_stream["/DestOutputProfile"] = icc_stream
        icc_stream["/Info"] = "sRGB Color Profile"

        # Add the OutputIntent to the PDF root dictionary
        root = pdf.Root
        if "/OutputIntents" not in root:
            root["/OutputIntents"] = pikepdf.Array()
        root["/OutputIntents"].append(icc_stream)

        # Step 3: Fix the trailer and add the File Identifiers (ID entry)
        id_string = hashlib.md5(os.urandom(16)).hexdigest().encode("utf-8")
        pdf.trailer["/ID"] = pikepdf.Array([id_string, id_string])

        # Save the final modified PDF
        pdf.save(final_output_pdf)


def process_pdfs(input_files, output_dir, icc_profile_path):
    """
    Process a list of PDF files by embedding fonts and ICC profile.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    for input_file in input_files:
        base_name = os.path.basename(input_file)
        intermediate_pdf = os.path.join(output_dir, f"intermediate_{base_name}")
        final_output_pdf = os.path.join(output_dir, f"final_{base_name}")
        
        # Embed fonts with Ghostscript
        embed_fonts_with_ghostscript(input_file, intermediate_pdf)
        
        # Embed ICC profile and fix trailer
        embed_icc_profile_and_fix_trailer(intermediate_pdf, icc_profile_path, final_output_pdf)
        
        # Remove intermediate file
        os.remove(intermediate_pdf)
        
    print(f"All PDFs processed and saved in {output_dir}")

def process_pdfs_with_progress(input_files, output_dir, icc_profile_path):
    """
    Process a list of PDF files by embedding fonts and ICC profile with a progress bar.
    """
    from rich.progress import Progress
    from rich.console import Console

    os.makedirs(output_dir, exist_ok=True)
    console = Console()
    
    with Progress() as progress:
        task = progress.add_task("[green]Processing PDFs...", total=len(input_files))
        
        for input_file in input_files:
            base_name = os.path.basename(input_file)
            intermediate_pdf = os.path.join(output_dir, f"intermediate_{base_name}")
            final_output_pdf = os.path.join(output_dir, f"final_{base_name}")
            
            # Embed fonts with Ghostscript
            embed_fonts_with_ghostscript(input_file, intermediate_pdf)
            
            # Embed ICC profile and fix trailer
            embed_icc_profile_and_fix_trailer(intermediate_pdf, icc_profile_path, final_output_pdf)
            
            # Remove intermediate file
            os.remove(intermediate_pdf)
            
            progress.update(task, advance=1)
    
    console.print(f"[bold green]All PDFs processed and saved in {output_dir}[/bold green]")

def process_multiple_pdfs(input_files, output_dir, icc_profile_path):
    """
    Process a list of PDF files by embedding fonts and ICC profile.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Embed fonts with Ghostscript for all files at once
    intermediate_pdfs = embed_fonts_with_ghostscript_multi(input_files, output_dir)
    
    for input_file, intermediate_pdf in zip(input_files, intermediate_pdfs):
        base_name = os.path.basename(input_file)
        final_output_pdf = os.path.join(output_dir, base_name)
        
        # Embed ICC profile and fix trailer
        embed_icc_profile_and_fix_trailer(intermediate_pdf, icc_profile_path, final_output_pdf)
        
        # Remove intermediate file
        os.remove(intermediate_pdf)
        
    print(f"All PDFs processed and saved in {output_dir}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Process PDF files to embed fonts and ICC profile.")
    parser.add_argument("-i", "--input_dir", required=True, help="Input directory containing PDF files to process")
    parser.add_argument("-o", "--output_dir", required=True, help="Output directory for processed PDFs")
    parser.add_argument("-p", "--icc_profile", help="Path to ICC profile", default='sRGB_ICC_v4_Appearance.icc')


    args = parser.parse_args()
    input_dir = Path(args.input_dir).expanduser()
    if not input_dir.is_dir():
        raise ValueError(f"Input directory {input_dir} does not exist")
    files = list(input_dir.glob("*.pdf"))
    output_dir = Path(args.output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    process_pdfs_with_progress(files, output_dir, args.icc_profile)
    #process_multiple_pdfs(files, output_dir, args.icc_profile)

if __name__ == "__main__":
    main()

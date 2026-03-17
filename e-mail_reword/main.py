from utils.summarize import original_emails

def main():
    try:
        # Read entire file as text
        with open("initial_email.txt", "r", encoding="utf-8") as f:
            email_text = f.read()
            
        # Treat whitespace-only content as empty
        if not email_text.strip():
            raise ValueError("initial_email.txt is empty or contains only whitespace")

        reworded = original_emails(email_text)
        print("\nReworded E-mail:\n")
        print(reworded)
        
        # Write the output to final_email.txt (overwrite each run)
        with open("final_email.txt", "w", encoding="utf-8") as out:
            # Ensure the file ends with a newline for POSIX-friendly text files
            out.write(reworded if reworded.endswith("\n") else reworded + "\n")

        print("\nSaved to final_email.txt")
        
    except Exception as e:
        print(f"Error rewording the e-mail: {e}")

if __name__ == "__main__":
    main()
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenizerser
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextPa
from sumy.summarizers.lsa import LsaSummarizer

# Ensure nltk resources are downloaded
nltk.download('punkt')
nltk.download('stopwords')

# Function to download image
def download_image(image_url, folder):
    try:
        if not os.path.exists(folder):
            os.makedirs(folder)

        img_response = requests.get(image_url, stream=True)
        if img_response.status_code == 200:
            img_name = os.path.join(folder, os.path.basename(image_url))
            with open(img_name, 'wb') as img_file:
                for chunk in img_response.iter_content(1024):
                    img_file.write(chunk)
            return f"Downloaded: {img_name}"
        else:
            return f"Failed to download image: {image_url}"
    except Exception as e:
        return f"Error downloading image {image_url}: {e}"

# Function to scrape and save content
def scrape_and_save(url, save_folder):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None, f"Failed to retrieve webpage. Status code: {response.status_code}"

        soup = BeautifulSoup(response.content, 'html.parser')
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        # Save HTML content
        html_file_path = os.path.join(save_folder, 'index.html')
        with open(html_file_path, 'w', encoding='utf-8') as html_file:
            html_file.write(str(soup))

        # Save text content
        all_text = soup.get_text(separator="\n", strip=True)
        csv_file_path = os.path.join(save_folder, 'all_text_content.csv')
        with open(csv_file_path, mode='w', encoding='utf-8', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Content"])
            for line in all_text.split("\n"):
                if line.strip():
                    writer.writerow([line])

        # Download images
        image_folder = os.path.join(save_folder, 'images')
        messages = []
        images = soup.find_all('img')
        for img in images:
            img_url = img.get('src')
            if img_url:
                img_url = urljoin(url, img_url)
                messages.append(download_image(img_url, image_folder))

        return all_text, "\n".join(messages)
    except Exception as e:
        return None, f"Error while processing: {e}"

# Function to get top frequency words
def get_top_words(text, num_words=10):
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text.lower())
    words = [word for word in words if word.isalpha() and word not in stop_words]
    word_counts = Counter(words)
    return word_counts.most_common(num_words)

# Function to summarize text
def summarize_text(text, num_sentences=3):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, num_sentences)
    return " ".join(str(sentence) for sentence in summary)

# GUI functions
def start_scraping():
    url = url_entry.get()
    if not url:
        messagebox.showwarning("Input Error", "Please enter a URL.")
        return

    save_folder = filedialog.askdirectory(title="Select Folder to Save Content")
    if not save_folder:
        messagebox.showwarning("Folder Selection", "Please select a folder to save the content.")
        return

    text, messages = scrape_and_save(url, save_folder)
    if not text:
        messagebox.showerror("Error", messages)
        return

    messagebox.showinfo("Success", f"Scraping completed!\nImages and content saved in: {save_folder}")
    ask_further_options(text)

def ask_further_options(text):
    def process_option():
        if option.get() == "Top Frequency Words":
            num_words = int(word_count_entry.get())
            top_words = get_top_words(text, num_words)
            display_results("\n".join(f"{word}: {count}" for word, count in top_words))
        elif option.get() == "Text Summarizer":
            num_sentences = int(sentence_count_entry.get())
            summary = summarize_text(text, num_sentences)
            display_results(summary)

    options_window = tk.Toplevel()
    options_window.title("Further Options")
    options_window.geometry("600x300")
    options_window.configure(bg="#f9f9f9")

    ttk.Label(options_window, text="Choose an Action", font=("Verdana", 14, "bold"), background="#f9f9f9").pack(pady=10)

    # Action selection
    frame = ttk.Frame(options_window)
    frame.pack(pady=10)
    option = ttk.Combobox(frame, values=["Top Frequency Words", "Text Summarizer"], state="readonly")
    option.set("Top Frequency Words")
    option.pack(side=tk.LEFT, padx=10)

    word_count_label = ttk.Label(frame, text="Top Words:", font=("Verdana", 10))
    word_count_label.pack(side=tk.LEFT, padx=5)
    word_count_entry = ttk.Entry(frame, width=5)
    word_count_entry.insert(0, "10")
    word_count_entry.pack(side=tk.LEFT)

    sentence_count_label = ttk.Label(frame, text="Summary Sentences:", font=("Verdana", 10))
    sentence_count_label.pack(side=tk.LEFT, padx=5)
    sentence_count_entry = ttk.Entry(frame, width=5)
    sentence_count_entry.insert(0, "3")
    sentence_count_entry.pack(side=tk.LEFT)

    ttk.Button(options_window, text="Process", command=process_option).pack(pady=20)

def display_results(results):
    result_window = tk.Toplevel()
    result_window.title("Results")
    result_window.geometry("800x500")
    result_window.configure(bg="#f9f9f9")

    header = ttk.Label(result_window, text="Results", font=("Verdana", 16, "bold"), background="#f9f9f9")
    header.pack(pady=10)

    result_text = scrolledtext.ScrolledText(result_window, wrap=tk.WORD, width=90, height=25, font=("Verdana", 10))
    result_text.pack(padx=20, pady=20)
    result_text.insert(tk.END, results)

def run_app():
    global url_entry

    app = tk.Tk()
    app.title("Web Scraper")
    app.geometry("800x500")
    app.configure(bg="#e3f2fd")

    header = ttk.Label(app, text="Web Scraper", font=("Verdana", 24, "bold"), background="#e3f2fd")
    header.pack(pady=20)

    frame = ttk.Frame(app, padding=20)
    frame.pack(pady=20, fill=tk.X)

    ttk.Label(frame, text="Enter URL:", font=("Verdana", 12)).pack(side=tk.LEFT, padx=10)
    url_entry = ttk.Entry(frame, width=60, font=("Verdana", 12))
    url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

    ttk.Button(app, text="Scrape and Save", command=start_scraping, style="Accent.TButton").pack(pady=30)

    # Adding styles
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Accent.TButton", font=("Verdana", 12), foreground="white", background="#1976d2")
    style.map("Accent.TButton", background=[("active", "#1565c0")])

    app.mainloop()

if __name__ == "__main__":
    run_app()

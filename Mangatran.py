import customtkinter as ctk
from tkinter import filedialog, messagebox
import numpy
import sys, os, requests, json, webbrowser, string, shutil
import easyocr
from manga_ocr import MangaOcr
import cv2
from deep_translator import GoogleTranslator
from matplotlib import pyplot as plt
from PIL import Image, ImageDraw, ImageFont

class MangaTran(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.geometry('500x600')
        self.title(f"Mangatran")
        self.eval('tk::PlaceWindow . center')

        self.grid_rowconfigure(0, weight=0)
        self.grid_columnconfigure(0, weight=1)
                
        self.inputFrame = ctk.CTkFrame(self, width=500, fg_color="transparent")
        self.inputFrame.grid_rowconfigure(0, weight=0)
        self.inputFrame.grid_columnconfigure(0, weight=0)
        self.inputFrame.grid(row=0, column=0)

        self.inputLabel = ctk.CTkLabel(master=self.inputFrame, width=20, height=20, text="Input Location", font=("Arial Bold", 14))
        self.inputLabel.grid(row=0, column=0, sticky="nw", padx=25, pady=(20, 5))

        self.inputTextbox = ctk.CTkTextbox(master=self.inputFrame, width=330, height=32, border_width=1, corner_radius=8, text_color="white")
        self.inputTextbox.grid(row=1, column=0, padx=20)
        self.inputTextbox.configure(state="disabled")
        
        self.inputButton = ctk.CTkButton(master=self.inputFrame, width=50, height=32, border_width=0, corner_radius=8, text="Import Image(s)", command=self.get_images)
        self.inputButton.grid(row=1, column=1, padx=(0, 25))
        
        
        
        self.languageLabel = ctk.CTkLabel(master=self, width=20, height=20, text="Detected Language", font=("Arial Bold", 14))
        self.languageLabel.grid(row=2, column=0, sticky="nw", padx=25, pady=(20, 5))
        
        self.languageCombobox = ctk.CTkComboBox(master=self, width=460, values=["Korean", "Japanese", "Simplified Chinese", "Traditional Chinese", "English"])
        self.languageCombobox.grid(row=3, column=0, sticky="nw", padx=20)
        
        self.confidenceLabel = ctk.CTkLabel(master=self, width=20, height=20, text="Confidence: (0.0) Increase the slider incase of \nFalse Positives or Multiple Detections", font=("Arial Bold", 14))
        self.confidenceLabel.grid(row=4, column=0, padx=25, sticky="nw", pady=(20, 5))
        
        self.confidenceSlider = ctk.CTkSlider(master=self, from_=0, to=1, number_of_steps=100, width=460, command=self.change_confidence)
        self.confidenceSlider.grid(row=5, column=0, sticky="nw", padx=20)
        self.confidenceSlider.set(0.0)
    
        self.optionsFrame = ctk.CTkFrame(self, width=500, fg_color="transparent")
        self.optionsFrame.grid_rowconfigure(0, weight=0)
        self.optionsFrame.grid_columnconfigure(0, weight=1)
        self.optionsFrame.grid(row=6, column=0)
        
        self.rawSwitch = ctk.CTkSwitch(master=self.optionsFrame, text="OCR", onvalue=1, offvalue=0)
        self.rawSwitch.grid(row=0, column=0, pady=(20, 0), padx=10)
        
        self.translateSwitch = ctk.CTkSwitch(master=self.optionsFrame, text="Translate", onvalue=1, offvalue=0)
        self.translateSwitch.grid(row=0, column=1, pady=(20, 0), padx=10)
        
        self.previewSwitch = ctk.CTkSwitch(master=self.optionsFrame, text="Preview Image(s)", onvalue=1, offvalue=0)
        self.previewSwitch.grid(row=1, column=0, pady=(20, 0), padx=10)
        
        self.processButton = ctk.CTkButton(master=self, width=120, height=32, corner_radius=8, text="Blast!", command=self.OCR)
        self.processButton.grid(row=7, column=0, pady=(100, 0))

    def get_images(self):
        path = filedialog.askopenfilenames(parent=self, title="Upload image(s)")
        self.inputTextbox.configure(state="normal")
        self.inputTextbox.delete("0.0", "end")
        self.inputTextbox.insert("0.0", path)
        self.inputTextbox.configure(state="disabled")
        
        
    def change_confidence(self, value):
        self.confidenceLabel.configure(text=f"Confidence: ({round(value, 2)})")
        
    
    def OCR(self):
        
        # Check if any images are imported
        imageInput = self.inputTextbox.get("0.0", "end").strip()
        if imageInput == "":
            messagebox.showerror("Error", "No images are inputed.")
            return
        
        
        # Get list of images to be OCR'd
        images = list(self.tk.splitlist(imageInput))
        
        # Options
        confidence = self.confidenceSlider.get()
        lang = self.languageCombobox.get()
        preview = self.previewSwitch.get()
        raw_export = self.rawSwitch.get()
        translate_export = self.translateSwitch.get()
        
        # Get language code
        if lang == "Korean":
            lang = "ko"
        elif lang == "Japanese":
            lang = "ja"
        elif lang == "Simplified Chinese":
            lang = "ch_sim"
        elif lang == "Traditional Chinese":
            lang = "ch_tra"
        elif lang == "English":
            lang = "en"
        
    
        for idx, image in enumerate(images):
            # Copies image and remove non-unicode characters
            if not image.isascii():
                name = ''.join(i for i in image if i in string.printable)

                if os.path.splitext(os.path.basename(name))[1] == '':
                    name = ""
                    extension = os.path.splitext(os.path.basename(name))[0]
                else:
                    name = os.path.splitext(os.path.basename(name))[0]
                    extension = os.path.splitext(os.path.basename(name))[1]
                
                name = os.path.join(os.path.dirname(image), name + str(idx) + extension)
                shutil.copy(image, name)
                image = name
            
            # OCR
            # print(image)
            # print(type(image))
            reader = easyocr.Reader([lang])
            result = reader.readtext(image)

            #MOCR
            img = Image.open(image)
            I = numpy.asarray(img)
            mocr = MangaOcr()
            # text_mocr = mocr(img)
            # print(type(img))
            # print(text_mocr)

            # Read the image
            img_rect = cv2.imread(image)
            img_temp = cv2.imread(image)
            h, w, c = img_temp.shape
            
            # Fill temp image with black
            img_temp = cv2.rectangle(img_temp, [0,0], [w, h], (0, 0, 0), -1)
            # inpainted_image = cv2.imread(image)
            img_copy = cv2.imread(image) 
            preview_boxes = cv2.imread(image)

            mOCR_list = []
            rects = []
            
            # For each detected text
            for r in result:
                
                # If the OCR text is above the CONFIDENCE
                if r[2] >= confidence:
                    
                    # saving Image rectangle coordinates
                    top_left = tuple(int(x) for x in tuple(r[0][0]))
                    bot_right = tuple(int(x) for x in tuple(r[0][2]))
                    # print("top_left",top_left)
                    # print("bot_right",bot_right)

                    # Compute the top right and bottom left coordinates
                    top_right = (bot_right[0], top_left[1])
                    bottom_left = (top_left[0], bot_right[1])
                    
                    # Crop the image according to the rectangles
                    x, y, w, h = top_left[0], top_left[1], bot_right[0] - top_left[0], bot_right[1] - top_left[1]
                    image_crop = I[y:y+h, x:x+w]
                    # Convert the NumPy array back to an image
                    image_crop = Image.fromarray(image_crop)
                    #OCR on each text rectangles
                    text_from_rect = mocr(image_crop)
                    mOCR_list.append(text_from_rect)
                
                    # Add rectangles to a list
                    rects.append((bot_right, top_left))
                    
                    # Draw a rectangle around the text
                    img_rect = cv2.rectangle(img_rect, top_left, bot_right, (0,255,0), 3)        
                    
                    # Whiten the area where the text is present.
                    img_white_rect = cv2.rectangle(img_copy, top_left, bot_right, (255,255,255), -1)

                    # # Fill text with white rectangle
                    # img_temp = cv2.rectangle(img_temp, top_left, bot_right, (255, 255, 255), -1)
                    # cv2.imshow('Original Image', img)
                    # cv2.imshow('Rectangle Image', img_white_rect)
                    # # Convert temp image to black and white for mask
                    # mask = cv2.cvtColor(img_temp, cv2.COLOR_BGR2GRAY)
                    
                    # # Inpainting the image --> Discontinued
                    # inpainted_image = cv2.inpaint(inpainted_image, mask, 3, cv2.INPAINT_TELEA)
            
                    # Draw a rectangle around the text
                    preview_boxes = cv2.rectangle(img_rect, top_left, bot_right, (0,255,0), 3)
                    
                    # Draw confidence level on detected text
                    cv2.putText(preview_boxes, str(round(r[2], 2)), top_left, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, 1)

                    # Code to write the translation back into the whited bubbles.

                    # define the text to write
                    translation = GoogleTranslator(source='auto', target='en').translate(text_from_rect)
                    # translation = translation.replace(" ", "\n")
                    # Define the font properties
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 0.2
                    font_color = (0, 0, 255)
                    thickness = 1
                    
                    top_left = tuple(map(lambda i, j: i - j, top_left, (0,0)))
                    rect_start = top_left
                    rect_end = bot_right
                    rect_color = (255, 0, 0)
                    rect_thickness = 1

                    # Draw the bounding rectangle onto the image
                    cv2.rectangle(I, rect_start, rect_end, rect_color, rect_thickness)
                    # Define the text position based on the bounding rectangle coordinates
                    text_size = cv2.getTextSize(translation, font, font_scale, thickness)[0]
                    x = rect_start[0] + int((rect_end[0] - rect_start[0] - text_size[0]) / 2)
                    y = rect_start[1] + int((rect_end[1] - rect_start[1] + text_size[1]) / 2)

                    # Write the text onto the image
                    cv2.putText(img_white_rect, translation, (x, y), font, font_scale, font_color, thickness)
            
            # Show all detected text and their confidence level
            if preview:
                plt.figure(figsize=(7, 7))
                plt.axis('off')
                plt.imshow(cv2.cvtColor(preview_boxes, cv2.COLOR_BGR2RGB))
                plt.show()
                    
            # Export raw list to a text file
            if raw_export:               
                # print(raw_list)
                self.exportRaw(image, mOCR_list, rects)
                # print(rects)
                # self.exportRaw_MOCR(image, text_mocr)
            
            # Export translated raw text to a text file
            if translate_export:
                raw = self.exportRaw(image, mOCR_list, rects)
                
                translation = GoogleTranslator(source='auto', target='en').translate(raw)
                        
                path = os.path.dirname(image)
                with open(os.path.join(path, os.path.splitext(os.path.basename(image))[0] + "_translated.txt"), 'w', encoding='UTF-8') as fp:
                    fp.write(translation)
                    fp.close()
            
            # Export image
            cv2.imwrite(image.replace(".png", "").replace(".jpg", "") + "_ocr.png", img_white_rect)
        
        messagebox.showinfo(title="Mangatran", message="Find your Translated Image in the Image Directory")
        self.inputTextbox.delete("0.0", "end")
    
    # Separating Axis Theorem to find intersecting rectangles.
    def intersect(self, top_right1, bottom_left1, top_right2, bottom_left2):    
        return not (top_right1[0] < bottom_left2[0] or bottom_left1[0] > top_right2[0] or top_right1[1] < bottom_left2[1] or bottom_left1[1] > top_right2[1])

    # Exports OCR from Image into a text file
    def exportRaw(self, image, list_words, rects):
        path = os.path.dirname(image)
        raw_string = ""
        with open(os.path.join(path, os.path.splitext(os.path.basename(image))[0] + "_OCR.txt"), 'w', encoding='UTF-8') as fp:
            for index, obj in enumerate(list_words):
                if index > 0:
                    if self.intersect(rects[index][0], rects[index][1], rects[index-1][0], rects[index-1][1]):
                        fp.write(f"{obj}")
                        raw_string += obj
                    else:
                        fp.write(f"\n{obj}")
                        raw_string += "\n" + obj
                else:
                    fp.write(f"{obj}")
                    raw_string += obj
            fp.close()
        return raw_string
    
    # def exportRaw_MOCR(self, image, text_mocr):
    #     path = os.path.dirname(image)
    #     with open(os.path.join(path, os.path.splitext(os.path.basename(image))[0] + "_raw.txt"), 'w', encoding='UTF-8') as fp:
    #         fp.write(text_mocr)
    #         fp.close()
    #     return text_mocr

if __name__ == "__main__":
    app = MangaTran()
    app.mainloop()



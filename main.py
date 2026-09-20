# ==========================================
# Kato KDP Auto-Framer
# Copyright (c) 2026 Mohamed Kato
# All Rights Reserved.
# ==========================================

import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar, Style
from PIL import Image, ImageOps
import threading

# ==========================================
# إعدادات أبعاد أمازون KDP
# ==========================================
# الأبعاد 8.5 × 11 بوصة مع إضافة مساحة النزف (Bleed)
WIDTH_INCHES = 8.625
HEIGHT_INCHES = 11.25
DPI = 300

# حساب المقاس بالبيكسل لضمان جودة 300 DPI
WIDTH_PX = int(WIDTH_INCHES * DPI)  # ~2588 بيكسل
HEIGHT_PX = int(HEIGHT_INCHES * DPI) # ~3375 بيكسل

class KDPFormatterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kato KDP Auto-Framer - by Mohamed Kato")
        self.root.geometry("550x380")
        self.root.configure(padx=20, pady=20)
        
        # واجهة المستخدم
        self.title_label = tk.Label(root, text="KDP PDF Generator", font=("Arial", 16, "bold"))
        self.title_label.pack(pady=(0, 15))
        
        desc = ("حدد المجلد الذي يحتوي على صور التلوين.\n"
                "البرنامج سيقوم بـ:\n"
                "1. التأكد من تحويلها كلها لأبيض وأسود (Grayscale).\n"
                "2. ضبط أبعادها بدقة إلى 8.625 × 11.25 بوصة (300 DPI).\n"
                "3. دمجها في ملف PDF مع وضع صفحة فارغة بعد كل رسمة.")
        self.desc_label = tk.Label(root, text=desc, justify="center", font=("Arial", 10))
        self.desc_label.pack(pady=(0, 20))
        
        self.folder_path = tk.StringVar()
        
        self.select_btn = tk.Button(root, text="اختر مجلد الصور...", command=self.select_folder, width=25, font=("Arial", 11))
        self.select_btn.pack(pady=10)
        
        self.path_label = tk.Label(root, textvariable=self.folder_path, fg="gray", wraplength=450)
        self.path_label.pack(pady=5)
        
        self.process_btn = tk.Button(root, text="بدء المعالجة واستخراج PDF", command=self.start_processing, width=25, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
        self.process_btn.pack(pady=15)
        
        # شريط التقدم (Progress bar)
        self.style = Style()
        self.style.theme_use('default')
        self.style.configure("TProgressbar", thickness=20)
        
        self.progress = Progressbar(root, orient=tk.HORIZONTAL, length=450, mode='determinate', style="TProgressbar")
        self.progress.pack(pady=10)
        
        self.status_label = tk.Label(root, text="البرنامج جاهز.", fg="blue", font=("Arial", 10))
        self.status_label.pack()

    def select_folder(self):
        folder = filedialog.askdirectory(title="اختر المجلد الذي يحتوي على الصور")
        if folder:
            self.folder_path.set(folder)
            self.status_label.config(text="تم اختيار المجلد. اضغط على 'بدء المعالجة'.")

    def start_processing(self):
        folder = self.folder_path.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showwarning("تنبيه", "يرجى اختيار مجلد صحيح أولاً.")
            return
            
        self.process_btn.config(state=tk.DISABLED)
        self.select_btn.config(state=tk.DISABLED)
        self.progress['value'] = 0
        self.status_label.config(text="جاري معالجة الصور... يرجى الانتظار.")
        
        # تشغيل العملية في خلفية (Thread) لعدم تجميد واجهة البرنامج
        threading.Thread(target=self.process_images, args=(folder,), daemon=True).start()

    def process_images(self, folder):
        try:
            valid_exts = ('.png', '.jpg', '.jpeg', '.webp')
            image_files = [f for f in os.listdir(folder) if f.lower().endswith(valid_exts)]
            
            if not image_files:
                self.root.after(0, self.finish_processing, False, "لم يتم العثور على أي صور في المجلد المختار.")
                return
            
            # ترتيب الملفات أبجدياً للحفاظ على الترتيب الصحيح للصفحات
            image_files.sort()
            
            pdf_pages = []
            # إنشاء صفحة بيضاء فارغة تماماً بنفس الأبعاد (تُستخدم كظهر للرسمة)
            blank_page = Image.new('L', (WIDTH_PX, HEIGHT_PX), 255)
            
            total_files = len(image_files)
            
            # حساب هوامش الأمان: الحد الأدنى لأمازون هو 0.375 بوصة
            # هذا سيعطينا أقصى حجم ممكن للصورة ليطابق تصميم Canva الأصلي
            MARGIN_PX = int(0.375 * DPI)
            SAFE_WIDTH_PX = WIDTH_PX - (2 * MARGIN_PX)
            SAFE_HEIGHT_PX = HEIGHT_PX - (2 * MARGIN_PX)
            
            for i, filename in enumerate(image_files):
                img_path = os.path.join(folder, filename)
                
                with Image.open(img_path) as img:
                    # 1. تحويل الصورة إلى تدرج رمادي (أبيض وأسود)
                    img_gray = img.convert('L')
                    
                    # 2. التدوير التلقائي (Auto-Rotate)
                    if img_gray.width > img_gray.height:
                        img_gray = img_gray.rotate(90, expand=True)
                        
                    # 3. اكتشاف الـ Frame الخارجي وقص المساحات البيضاء الوهمية
                    binary = img_gray.point(lambda p: 0 if p > 240 else 255)
                    bbox = binary.getbbox()
                    if bbox:
                        img_gray = img_gray.crop(bbox)
                    
                    # 4. تكبير الصورة لأقصى حد ممكن داخل منطقة الأمان دون تغيير نسبتها (Contain)
                    img_safe = ImageOps.contain(img_gray, (SAFE_WIDTH_PX, SAFE_HEIGHT_PX), method=Image.Resampling.LANCZOS)
                    
                    # 5. إنشاء صفحة بيضاء بحجم KDP الكامل (8.625x11.25)
                    page_canvas = Image.new('L', (WIDTH_PX, HEIGHT_PX), 255)
                    
                    # 6. حساب الإحداثيات لتوسيط الصورة تماماً في الورقة
                    offset_x = (WIDTH_PX - img_safe.width) // 2
                    offset_y = (HEIGHT_PX - img_safe.height) // 2
                    
                    # 7. لصق الرسمة فوق الصفحة البيضاء
                    page_canvas.paste(img_safe, (offset_x, offset_y))
                    
                    pdf_pages.append(page_canvas)
                    pdf_pages.append(blank_page) # إضافة الصفحة البيضاء خلف الرسمة
                
                # تحديث شريط التقدم
                progress_val = int(((i + 1) / total_files) * 100)
                self.root.after(0, self.update_progress, progress_val, f"جاري معالجة: {filename} ({i+1}/{total_files})")
            
            if pdf_pages:
                self.root.after(0, self.update_progress, 99, "جاري حفظ ملف الـ PDF النهائي... قد يستغرق الأمر بعض الوقت.")
                
                # مسار البرنامج: دعم استخراج المسار الصحيح عند تشغيله كملف exe
                import sys
                if getattr(sys, 'frozen', False):
                    app_dir = os.path.dirname(sys.executable)
                else:
                    app_dir = os.path.dirname(os.path.abspath(__file__))
                    
                pdf_dir = os.path.join(app_dir, "PDF")
                os.makedirs(pdf_dir, exist_ok=True)
                
                # استخراج اسم المجلد المختار لتسمية الكتاب به
                folder_name = os.path.basename(os.path.normpath(folder))
                if not folder_name:
                    folder_name = "Final_Coloring_Book"
                    
                # إضافة Timestamp لضمان عدم استبدال الملف القديم (Unique Name)
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                output_pdf = os.path.join(pdf_dir, f"{folder_name}_KDP_{timestamp}.pdf")
                
                # حفظ الصورة الأولى كملف PDF وإرفاق الباقي خلفها
                pdf_pages[0].save(
                    output_pdf, "PDF", resolution=300.0, save_all=True, append_images=pdf_pages[1:]
                )
                
                self.root.after(0, self.finish_processing, True, f"تم بنجاح!\nمسار الملف:\n{output_pdf}", pdf_dir, output_pdf)
            else:
                self.root.after(0, self.finish_processing, False, "فشلت معالجة الصور.")
                
        except Exception as e:
            self.root.after(0, self.finish_processing, False, f"حدث خطأ: {str(e)}")

    def update_progress(self, value, text):
        self.progress['value'] = value
        self.status_label.config(text=text)

    def finish_processing(self, success, message, pdf_dir=None, output_pdf=None):
        self.process_btn.config(state=tk.NORMAL)
        self.select_btn.config(state=tk.NORMAL)
        self.progress['value'] = 100 if success else 0
        self.status_label.config(text="اكتمل العمل!" if success else "فشلت العملية.")
        
        if success:
            messagebox.showinfo("نجاح", message)
            # فتح المجلد الذي يحتوي على ملف الـ PDF تلقائياً
            if pdf_dir and os.path.exists(pdf_dir):
                os.startfile(pdf_dir)
            # فتح ملف الـ PDF نفسه تلقائياً
            if output_pdf and os.path.exists(output_pdf):
                os.startfile(output_pdf)
        else:
            messagebox.showerror("خطأ", message)

if __name__ == "__main__":
    root = tk.Tk()
    app = KDPFormatterApp(root)
    root.mainloop()

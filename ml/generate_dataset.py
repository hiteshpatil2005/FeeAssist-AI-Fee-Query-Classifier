"""
FeeAssist AI — Dataset Generator & Curator

Constructs a balanced, diverse fee-query dataset across 10 intents and 3 languages:
English, Hindi, and Marathi.
"""

import csv
import os
import sys

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

DATA = [
    # ══════════════════════════════════════════════════════════════════════════
    # 1. FEE_STRUCTURE
    # ══════════════════════════════════════════════════════════════════════════
    # English
    ("What is the fee structure for Computer Science?", "FEE_STRUCTURE", "English"),
    ("How much is the total tuition fee for third year?", "FEE_STRUCTURE", "English"),
    ("Can you provide the breakdown of semester 5 college fees?", "FEE_STRUCTURE", "English"),
    ("What are the hostel and mess charges for this academic year?", "FEE_STRUCTURE", "English"),
    ("Tell me the annual fee for B.Tech program.", "FEE_STRUCTURE", "English"),
    ("How much is the tuition fee per semester?", "FEE_STRUCTURE", "English"),
    ("What are the laboratory and library fees included in total charges?", "FEE_STRUCTURE", "English"),
    ("Is there any separate examination fee payable?", "FEE_STRUCTURE", "English"),
    ("Where can I find the official fee schedule for 2026-27?", "FEE_STRUCTURE", "English"),
    ("What is the total cost of studying MBA here?", "FEE_STRUCTURE", "English"),
    ("Break down the development and gymkhana fees for me.", "FEE_STRUCTURE", "English"),
    ("How much do I need to pay for college admission?", "FEE_STRUCTURE", "English"),
    ("What are the semester charges for mechanical engineering?", "FEE_STRUCTURE", "English"),
    ("Explain the complete fee breakup for undergraduate students.", "FEE_STRUCTURE", "English"),
    ("Are bus and transport fees included in the college fee structure?", "FEE_STRUCTURE", "English"),
    ("What are the caution money and security deposit rates?", "FEE_STRUCTURE", "English"),
    # Hindi
    ("कंप्यूटर साइंस की फीस कितनी है?", "FEE_STRUCTURE", "Hindi"),
    ("कॉलेज का पूरा फीस स्ट्रक्चर क्या है?", "FEE_STRUCTURE", "Hindi"),
    ("तीसरे साल की ट्यूशन फीस कितनी लगती है?", "FEE_STRUCTURE", "Hindi"),
    ("क्या हॉस्टल और मेस का खर्च कॉलेज फीस में शामिल है?", "FEE_STRUCTURE", "Hindi"),
    ("बी.टेक का एक साल का खर्चा कितना आता है?", "FEE_STRUCTURE", "Hindi"),
    ("सेमेस्टर 5 की कुल फीस का विवरण बताएं।", "FEE_STRUCTURE", "Hindi"),
    ("लाइब्रेरी और लैब के लिए अलग से कितनी फीस देनी होगी?", "FEE_STRUCTURE", "Hindi"),
    ("क्या परीक्षा फॉर्म की फीस अलग से लगती है?", "FEE_STRUCTURE", "Hindi"),
    ("इस साल की नई फीस तालिका कहां देख सकते हैं?", "FEE_STRUCTURE", "Hindi"),
    ("इंजीनियरिंग की पूरी फीस की सूची दीजिए।", "FEE_STRUCTURE", "Hindi"),
    ("कॉलेज में एडमिशन के समय कितनी फीस भरनी पड़ती है?", "FEE_STRUCTURE", "Hindi"),
    ("ट्यूशन फीस और डेवलपमेंट फीस का ब्रेकअप क्या है?", "FEE_STRUCTURE", "Hindi"),
    ("डिग्री कोर्स का सालाना शुल्क कितना है?", "FEE_STRUCTURE", "Hindi"),
    # Marathi
    ("कॉलेजची फी रचना काय आहे?", "FEE_STRUCTURE", "Marathi"),
    ("कॉम्प्युटर सायन्ससाठी शैक्षणिक फी किती आहे?", "FEE_STRUCTURE", "Marathi"),
    ("तिसऱ्या वर्षाची एकूण ट्यूशन फी किती लागते?", "FEE_STRUCTURE", "Marathi"),
    ("हॉस्टेल आणि मेस चार्जेसचे तपशील द्या.", "FEE_STRUCTURE", "Marathi"),
    ("बीटेक अभ्यासक्रमाची वार्षिक फी किती आहे?", "FEE_STRUCTURE", "Marathi"),
    ("पाचव्या सेमिस्टरसाठी कॉलेज फी किती भरावी लागेल?", "FEE_STRUCTURE", "Marathi"),
    ("प्रयोगशाळा आणि वाचनालय शुल्क किती आकारले जाते?", "FEE_STRUCTURE", "Marathi"),
    ("परीक्षेचे शुल्क वेगळे भरायचे असते का?", "FEE_STRUCTURE", "Marathi"),
    ("नवीन शैक्षणिक वर्षाचे फी वेळापत्रक कुठे मिळेल?", "FEE_STRUCTURE", "Marathi"),
    ("प्रवेश घेताना सुरुवातीला किती रक्कम भरावी लागते?", "FEE_STRUCTURE", "Marathi"),
    ("अभियांत्रिकी शाखेचा पूर्ण फी ब्रेकअप सांगा.", "FEE_STRUCTURE", "Marathi"),
    ("कॉलेज फी मध्ये बस भाडे समाविष्ट आहे का?", "FEE_STRUCTURE", "Marathi"),

    # ══════════════════════════════════════════════════════════════════════════
    # 2. PENDING_FEE
    # ══════════════════════════════════════════════════════════════════════════
    # English
    ("How much fee is remaining for my account?", "PENDING_FEE", "English"),
    ("What is my current pending fee balance?", "PENDING_FEE", "English"),
    ("How much do I still owe to the college?", "PENDING_FEE", "English"),
    ("Tell me my outstanding fee balance for semester 5.", "PENDING_FEE", "English"),
    ("Do I have any unpaid balance left?", "PENDING_FEE", "English"),
    ("Check my pending fees for the current academic year.", "PENDING_FEE", "English"),
    ("How much fee do I need to pay to clear all dues?", "PENDING_FEE", "English"),
    ("Is there any balance amount pending against my student ID?", "PENDING_FEE", "English"),
    ("What is my remaining dues after the last payment?", "PENDING_FEE", "English"),
    ("Please tell me my unpaid college tuition amount.", "PENDING_FEE", "English"),
    ("Are there any pending hostel charges on my account?", "PENDING_FEE", "English"),
    ("How much fee is still due for this term?", "PENDING_FEE", "English"),
    ("I want to verify if any balance is pending on my profile.", "PENDING_FEE", "English"),
    ("How much outstanding payment is shown on my portal?", "PENDING_FEE", "English"),
    ("Show my pending fee breakdown.", "PENDING_FEE", "English"),
    # Hindi
    ("मेरी फीस कितनी बाकी है?", "PENDING_FEE", "Hindi"),
    ("क्या मेरी कोई फीस अभी भी बकाया है?", "PENDING_FEE", "Hindi"),
    ("पांचवें सेमेस्टर की कितनी रकम देना बाकी है?", "PENDING_FEE", "Hindi"),
    ("मुझे कॉलेज को अभी कितने पैसे देने हैं?", "PENDING_FEE", "Hindi"),
    ("मेरे खाते में बकाया फीस की जानकारी दीजिए।", "PENDING_FEE", "Hindi"),
    ("क्या मेरा कोई ट्यूशन शुल्क बाकी रह गया है?", "PENDING_FEE", "Hindi"),
    ("पिछला पेमेंट करने के बाद अब कितना शेष बचा है?", "PENDING_FEE", "Hindi"),
    ("कुल बकाया राशि कितनी दिख रही है?", "PENDING_FEE", "Hindi"),
    ("चेक करके बताएं कि मुझे अभी कितने रुपये भरने हैं।", "PENDING_FEE", "Hindi"),
    ("क्या इस सेमेस्टर का कोई पेंडिंग अमाउंट है?", "PENDING_FEE", "Hindi"),
    ("मेरी अनपेड फीस का स्टेटस क्या है?", "PENDING_FEE", "Hindi"),
    ("हॉस्टल की कोई फीस बाकी है क्या?", "PENDING_FEE", "Hindi"),
    ("क्या सेकंड इंस्टॉलमेंट की पेंडिंग फीस बाकी है?", "PENDING_FEE", "Hindi"),
    # Marathi
    ("माझी किती फी बाकी आहे?", "PENDING_FEE", "Marathi"),
    ("माझ्या खात्यावर काही थकबाकी आहे का?", "PENDING_FEE", "Marathi"),
    ("चालू सेमिस्टरची शिल्लक फी किती भरायची राहिली आहे?", "PENDING_FEE", "Marathi"),
    ("कॉलेजची किती रक्कम भरणे बाकी आहे ते सांगा.", "PENDING_FEE", "Marathi"),
    ("गेल्या वेळेस भरल्यानंतर आता किती फी शिल्लक आहे?", "PENDING_FEE", "Marathi"),
    ("थकबाकी शुल्काचा संपूर्ण तपशील द्या.", "PENDING_FEE", "Marathi"),
    ("माझ्या विद्यार्थी आयडीवर किती फी बाकी दिसते?", "PENDING_FEE", "Marathi"),
    ("सर्व देणी पूर्ण करण्यासाठी मला किती रुपये भरावे लागतील?", "PENDING_FEE", "Marathi"),
    ("पाचव्या सत्राची प्रलंबित फी किती आहे?", "PENDING_FEE", "Marathi"),
    ("माझे काही कॉलेज शुल्क देणे बाकी आहे का?", "PENDING_FEE", "Marathi"),
    ("थकबाकी रक्कम कधीपर्यंत क्लिअर करायची आहे?", "PENDING_FEE", "Marathi"),
    ("परीक्षा शुल्क बाकी आहे की भरले गेले आहे?", "PENDING_FEE", "Marathi"),

    # ══════════════════════════════════════════════════════════════════════════
    # 3. PAYMENT_STATUS
    # ══════════════════════════════════════════════════════════════════════════
    # English
    ("Did my fee payment go through successfully?", "PAYMENT_STATUS", "English"),
    ("What is the status of my recent transaction?", "PAYMENT_STATUS", "English"),
    ("Check status of transaction ID TXN984210482.", "PAYMENT_STATUS", "English"),
    ("My UPI fee payment was deducted but showing pending.", "PAYMENT_STATUS", "English"),
    ("Has my college fee payment been updated in the portal?", "PAYMENT_STATUS", "English"),
    ("Did the finance office receive my RTGS transfer?", "PAYMENT_STATUS", "English"),
    ("Verify if my semester fee payment was approved.", "PAYMENT_STATUS", "English"),
    ("Why is my fee payment still showing in progress?", "PAYMENT_STATUS", "English"),
    ("Check whether my online payment was confirmed.", "PAYMENT_STATUS", "English"),
    ("Is my payment status marked as completed or failed?", "PAYMENT_STATUS", "English"),
    ("I paid my tuition fee yesterday, is it verified now?", "PAYMENT_STATUS", "English"),
    ("Money got debited from my bank account, is my fee cleared?", "PAYMENT_STATUS", "English"),
    ("Check the verification status of my bank challan.", "PAYMENT_STATUS", "English"),
    ("Status of fee payment made through Net Banking.", "PAYMENT_STATUS", "English"),
    ("Was my card payment credited to the college account?", "PAYMENT_STATUS", "English"),
    ("Has the transaction TXN192847192 been marked successful?", "PAYMENT_STATUS", "English"),
    # Hindi
    ("मेरी फीस जमा हुई या नहीं?", "PAYMENT_STATUS", "Hindi"),
    ("मेरे पेमेंट का स्टेटस क्या है?", "PAYMENT_STATUS", "Hindi"),
    ("पैसे बैंक से कट गए लेकिन पोर्टल पर पेंडिंग दिखा रहा है।", "PAYMENT_STATUS", "Hindi"),
    ("ट्रांजैक्शन आईडी TXN192847192 का स्टेटस चेक करें।", "PAYMENT_STATUS", "Hindi"),
    ("क्या मेरी फीस कॉलेज को प्राप्त हो गई है?", "PAYMENT_STATUS", "Hindi"),
    ("मेरा यूपीआई पेमेंट सक्सेसफुल हुआ या फेल?", "PAYMENT_STATUS", "Hindi"),
    ("क्या मेरा बैंक ट्रांसफर कॉलेज रिकॉर्ड में अपडेट हो गया?", "PAYMENT_STATUS", "Hindi"),
    ("मैंने कल फीस भरी थी, क्या वह अप्रूव हो गई?", "PAYMENT_STATUS", "Hindi"),
    ("फीस भुगतान की स्थिति बताएं।", "PAYMENT_STATUS", "Hindi"),
    ("पोर्टल पर मेरी फीस सबमिट दिखा रहा है या नहीं?", "PAYMENT_STATUS", "Hindi"),
    ("चालान जमा करने के बाद स्टेटस कब अपडेट होगा?", "PAYMENT_STATUS", "Hindi"),
    ("क्या मेरा ऑनलाइन पेमेंट वेरीफाई हो गया है?", "PAYMENT_STATUS", "Hindi"),
    # Marathi
    ("माझी फी जमा झाली आहे का?", "PAYMENT_STATUS", "Marathi"),
    ("माझ्या पेमेंटची सध्याची स्थिती काय आहे?", "PAYMENT_STATUS", "Marathi"),
    ("बँकेतून पैसे कापले गेले पण पोर्टलवर अजून पेंडिंग दिसतेय.", "PAYMENT_STATUS", "Marathi"),
    ("माझे ऑनलाइन फी पेमेंट यशस्वी झाले की नाही ते तपासा.", "PAYMENT_STATUS", "Marathi"),
    ("कॉलेजला माझा युपीआय व्यवहार मिळाला का?", "PAYMENT_STATUS", "Marathi"),
    ("व्यवहार आयडी तपासून फी स्टेटस सांगा.", "PAYMENT_STATUS", "Marathi"),
    ("मी काल भरलेली फी कॉलेजने मंजूर केली का?", "PAYMENT_STATUS", "Marathi"),
    ("माझे बँक ट्रान्सफर पोर्टलवर अपडेट झाले आहे का?", "PAYMENT_STATUS", "Marathi"),
    ("फी भरल्याची खात्री कशी करावी?", "PAYMENT_STATUS", "Marathi"),
    ("पेमेंट पूर्ण झाले की अयशस्वी झाले ते दाखवा.", "PAYMENT_STATUS", "Marathi"),
    ("चालान भरल्यानंतर स्टेटस केव्हा क्लिअर होईल?", "PAYMENT_STATUS", "Marathi"),
    ("माझे कालचे पेमेंट कॉलेजच्या सिस्टीममध्ये दिसत आहे का?", "PAYMENT_STATUS", "Marathi"),

    # ══════════════════════════════════════════════════════════════════════════
    # 4. PAYMENT_HISTORY
    # ══════════════════════════════════════════════════════════════════════════
    # English
    ("Show my complete fee payment history.", "PAYMENT_HISTORY", "English"),
    ("When did I make my last fee payment?", "PAYMENT_HISTORY", "English"),
    ("List all my past fee transactions with dates and amounts.", "PAYMENT_HISTORY", "English"),
    ("I want to see the record of fees paid in previous semesters.", "PAYMENT_HISTORY", "English"),
    ("How much total money have I paid to the college so far?", "PAYMENT_HISTORY", "English"),
    ("Give me the history of payments made in 2025.", "PAYMENT_HISTORY", "English"),
    ("Show payments made for Semester 4 and Semester 3.", "PAYMENT_HISTORY", "English"),
    ("Can I get a summary of all my fee transactions till date?", "PAYMENT_HISTORY", "English"),
    ("What was the date of my first installment payment?", "PAYMENT_HISTORY", "English"),
    ("Show me the records of all UPI and Net Banking payments.", "PAYMENT_HISTORY", "English"),
    ("Display my fee clearance records from first year to now.", "PAYMENT_HISTORY", "English"),
    ("Where can I view my older payment logs?", "PAYMENT_HISTORY", "English"),
    ("Show details of the 50000 rupees payment made in August.", "PAYMENT_HISTORY", "English"),
    ("List of previous fee receipts and payment dates.", "PAYMENT_HISTORY", "English"),
    ("Did I pay through RTGS or UPI for my third semester fee?", "PAYMENT_HISTORY", "English"),
    ("Check the date and transaction ID of my last year fee submission.", "PAYMENT_HISTORY", "English"),
    # Hindi
    ("मेरी पुरानी फीस के सारे पेमेंट दिखाओ।", "PAYMENT_HISTORY", "Hindi"),
    ("मैंने पिछली बार फीस कब भरी थी?", "PAYMENT_HISTORY", "Hindi"),
    ("अब तक कॉलेज को कुल कितने रुपये दिए हैं?", "PAYMENT_HISTORY", "Hindi"),
    ("पिछले सेमेस्टर में भरे गए भुगतानों का रिकॉर्ड दिखाएं।", "PAYMENT_HISTORY", "Hindi"),
    ("मेरी फीस भुगतान की पूरी हिस्ट्री निकालें।", "PAYMENT_HISTORY", "Hindi"),
    ("सेमेस्टर 4 की फीस मैंने किस तारीख को भरी थी?", "PAYMENT_HISTORY", "Hindi"),
    ("सभी पिछले ट्रांजैक्शन की सूची देखें।", "PAYMENT_HISTORY", "Hindi"),
    ("2024 और 2025 में हुए पेमेंट का ब्योरा दें।", "PAYMENT_HISTORY", "Hindi"),
    ("क्या मैं अपने पुराने पेमेंट रिकॉर्ड देख सकता हूँ?", "PAYMENT_HISTORY", "Hindi"),
    ("पहले साल से अब तक कितने पैसे जमा किए हैं?", "PAYMENT_HISTORY", "Hindi"),
    ("अगस्त में भरे गए 50000 रुपये का ट्रांजैक्शन विवरण दिखाएं।", "PAYMENT_HISTORY", "Hindi"),
    ("मेरे पुराने फी चालान का रिकॉर्ड निकालें।", "PAYMENT_HISTORY", "Hindi"),
    # Marathi
    ("माझ्या सर्व जुन्या पेमेंटचा इतिहास दाखवा.", "PAYMENT_HISTORY", "Marathi"),
    ("मी शेवटची फी कधी भरली होती?", "PAYMENT_HISTORY", "Marathi"),
    ("आतापर्यंत मी एकूण किती फी भरली आहे?", "PAYMENT_HISTORY", "Marathi"),
    ("मागील सत्रात भरलेल्या सर्व पावत्यांचे रेकॉर्ड दाखवा.", "PAYMENT_HISTORY", "Marathi"),
    ("माझ्या फी भरणा इतिहासाची यादी द्या.", "PAYMENT_HISTORY", "Marathi"),
    ("चौथ्या सेमिस्टरची फी कोणत्या तारखेला भरली होती?", "PAYMENT_HISTORY", "Marathi"),
    ("गेल्या वर्षी केलेल्या सर्व व्यवहारांची माहिती हवी आहे.", "PAYMENT_HISTORY", "Marathi"),
    ("पहिल्या वर्षापासून आतापर्यंत भरलेल्या शुल्काचा तपशील.", "PAYMENT_HISTORY", "Marathi"),
    ("मी भरलेल्या रकमेची जुनी यादी कुठे दिसेल?", "PAYMENT_HISTORY", "Marathi"),
    ("मागील व्यवहारांचे दिनांक आणि रकमा दाखवा.", "PAYMENT_HISTORY", "Marathi"),
    ("५०,००० रुपये भरल्याची तारीख कोणती होती?", "PAYMENT_HISTORY", "Marathi"),
    ("मागील वर्षीच्या बँक ट्रान्सफरचा रेकॉर्ड दाखवा.", "PAYMENT_HISTORY", "Marathi"),

    # ══════════════════════════════════════════════════════════════════════════
    # 5. DUE_DATE
    # ══════════════════════════════════════════════════════════════════════════
    # English
    ("When is the last date to pay my fees?", "DUE_DATE", "English"),
    ("What is the fee payment deadline for semester 5?", "DUE_DATE", "English"),
    ("Until when can I pay my remaining fee without penalty?", "DUE_DATE", "English"),
    ("What is the late fee charge if I pay after the due date?", "DUE_DATE", "English"),
    ("Is there any extension on the college fee payment deadline?", "DUE_DATE", "English"),
    ("Tell me the exact due date for term fees.", "DUE_DATE", "English"),
    ("What is the penalty per day for late fee submission?", "DUE_DATE", "English"),
    ("When does the fee payment window close for this academic session?", "DUE_DATE", "English"),
    ("Can the due date be extended for students facing financial issues?", "DUE_DATE", "English"),
    ("By which date must hostel fees be cleared?", "DUE_DATE", "English"),
    ("Is tomorrow the last date to deposit semester charges?", "DUE_DATE", "English"),
    ("When is the final date for paying the examination fees?", "DUE_DATE", "English"),
    ("What happens if I miss the 15th November deadline?", "DUE_DATE", "English"),
    ("Check upcoming payment due dates for my branch.", "DUE_DATE", "English"),
    ("What is the cutoff date for depositing the term fees?", "DUE_DATE", "English"),
    # Hindi
    ("फीस भरने की आखिरी तारीख क्या है?", "DUE_DATE", "Hindi"),
    ("पांचवें सेमेस्टर की फीस कब तक जमा करनी है?", "DUE_DATE", "Hindi"),
    ("अगर ड्यू डेट के बाद फीस भरी तो कितना जुर्माना लगेगा?", "DUE_DATE", "Hindi"),
    ("क्या फीस भरने की अंतिम तिथि आगे बढ़ाई गई है?", "DUE_DATE", "Hindi"),
    ("बिना लेट फीस के कब तक भुगतान कर सकते हैं?", "DUE_DATE", "Hindi"),
    ("कॉलेज फीस जमा करने की लास्ट डेट बताएं।", "DUE_DATE", "Hindi"),
    ("लेट फीस कितने रुपये प्रतिदिन लगती है?", "DUE_DATE", "Hindi"),
    ("परीक्षा शुल्क जमा करने की आखिरी तिथि क्या है?", "DUE_DATE", "Hindi"),
    ("हॉस्टल फीस जमा करने का अंतिम दिन कब है?", "DUE_DATE", "Hindi"),
    ("क्या 15 नवंबर के बाद भी फीस भर सकते हैं?", "DUE_DATE", "Hindi"),
    ("अगले सेमेस्टर की डेडलाइन क्या तय की गई है?", "DUE_DATE", "Hindi"),
    ("लास्ट डेट निकल जाने पर क्या होगा?", "DUE_DATE", "Hindi"),
    ("अंतिम तिथि से पहले फीस भरने पर कोई छूट है क्या?", "DUE_DATE", "Hindi"),
    # Marathi
    ("फी भरण्याची शेवटची तारीख कोणती आहे?", "DUE_DATE", "Marathi"),
    ("चालू सेमिस्टरची फी कधीपर्यंत भरावी लागेल?", "DUE_DATE", "Marathi"),
    ("मुदतीनंतर फी भरल्यास किती दंड आकारला जाईल?", "DUE_DATE", "Marathi"),
    ("फी भरण्यासाठी मुदतवाढ मिळाली आहे का?", "DUE_DATE", "Marathi"),
    ("कोणत्या तारखेपर्यंत विलंब शुल्काशिवाय फी भरता येईल?", "DUE_DATE", "Marathi"),
    ("परीक्षा फी जमा करण्याची अखेरची तारीख सांगा.", "DUE_DATE", "Marathi"),
    ("हॉस्टेल शुल्काची डेडलाइन कधी संपणार आहे?", "DUE_DATE", "Marathi"),
    ("१५ नोव्हेंबरपर्यंत फी भरणे अनिवार्य आहे का?", "DUE_DATE", "Marathi"),
    ("उशिरा फी भरल्यास दिवसाला किती लेट फी लागते?", "DUE_DATE", "Marathi"),
    ("फी भरण्याचा शेवटचा दिवस कोणता आहे?", "DUE_DATE", "Marathi"),
    ("अंतिम मुदत हुकल्यास परीक्षेला बसू दिले जाईल का?", "DUE_DATE", "Marathi"),
    ("मुदतवाढीचा नवीन जीआर किंवा परिपत्रक आले आहे का?", "DUE_DATE", "Marathi"),

    # ══════════════════════════════════════════════════════════════════════════
    # 6. INSTALLMENT
    # ══════════════════════════════════════════════════════════════════════════
    # English
    ("Can I pay in four quarterly installments?", "INSTALLMENT", "English"),
    ("Can I pay my fees in installments?", "INSTALLMENT", "English"),
    ("How many installments are allowed for semester fees?", "INSTALLMENT", "English"),
    ("What is the process to apply for fee installment facility?", "INSTALLMENT", "English"),
    ("Can I pay 50% fees now and the rest after two months?", "INSTALLMENT", "English"),
    ("What is the amount of the second installment?", "INSTALLMENT", "English"),
    ("Are there any extra charges or interest for paying in parts?", "INSTALLMENT", "English"),
    ("How do I split my 75000 tuition fee into three installments?", "INSTALLMENT", "English"),
    ("Can I pay in two equal installments for this semester?", "INSTALLMENT", "English"),
    ("Is installment payment option available for open category students?", "INSTALLMENT", "English"),
    ("Whom should I contact in the accounts department for installment approval?", "INSTALLMENT", "English"),
    ("What are the installment payment dates for 2026?", "INSTALLMENT", "English"),
    ("Can hostel fees also be divided into installments?", "INSTALLMENT", "English"),
    ("I want to pay half my fee today and remaining next month.", "INSTALLMENT", "English"),
    ("Tell me the installment breakdown for annual tuition fees.", "INSTALLMENT", "English"),
    # Hindi
    ("क्या मैं फीस किस्तों में भर सकता हूँ?", "INSTALLMENT", "Hindi"),
    ("कॉलेज फीस की कितनी किस्तें हो सकती हैं?", "INSTALLMENT", "Hindi"),
    ("किस्तों में फीस भरने की क्या प्रक्रिया है?", "INSTALLMENT", "Hindi"),
    ("क्या मैं आधी फीस अभी और आधी अगले महीने दे सकता हूँ?", "INSTALLMENT", "Hindi"),
    ("दूसरी किस्त का भुगतान कब और कितना करना होगा?", "INSTALLMENT", "Hindi"),
    ("क्या किस्तों में भरने पर कोई अतिरिक्त चार्ज लगता है?", "INSTALLMENT", "Hindi"),
    ("75000 की फीस को 3 किस्तों में कैसे बांटें?", "INSTALLMENT", "Hindi"),
    ("इंस्टॉलमेंट सुविधा के लिए एप्लीकेशन कहां देनी होगी?", "INSTALLMENT", "Hindi"),
    ("क्या हॉस्टल की फीस भी किस्तों में दी जा सकती है?", "INSTALLMENT", "Hindi"),
    ("मुझे फीस पार्ट पेमेंट में जमा करनी है, क्या यह मुमकिन है?", "INSTALLMENT", "Hindi"),
    ("क्या गरीब छात्रों को 4 किस्तों की छूट मिल सकती है?", "INSTALLMENT", "Hindi"),
    ("फीस को दो बार में भरने की अनुमति कैसे लें?", "INSTALLMENT", "Hindi"),
    ("क्या तीसरी किस्त परीक्षा से पहले भरनी जरूरी है?", "INSTALLMENT", "Hindi"),
    # Marathi
    ("फी हप्त्यांमध्ये भरता येईल का?", "INSTALLMENT", "Marathi"),
    ("कॉलेज फी चे किती हप्ते करता येतात?", "INSTALLMENT", "Marathi"),
    ("हप्त्याने फी भरण्यासाठी अर्ज कसा करावा?", "INSTALLMENT", "Marathi"),
    ("अर्धी फी आता आणि उर्वरित दोन महिन्यांनी भरता येईल का?", "INSTALLMENT", "Marathi"),
    ("दुसऱ्या हप्त्याची रक्कम किती आणि कधी भरायची आहे?", "INSTALLMENT", "Marathi"),
    ("हप्त्यांमध्ये फी भरल्यास काही जास्तीचा आकार लागतो का?", "INSTALLMENT", "Marathi"),
    ("वार्षिक शुल्काचे दोन भागात विभाजन करता येईल का?", "INSTALLMENT", "Marathi"),
    ("हप्त्याची सवलत मिळवण्यासाठी कोणाशी संपर्क साधावा?", "INSTALLMENT", "Marathi"),
    ("हॉस्टेलची फी हप्त्यांमध्ये जमा करता येते का?", "INSTALLMENT", "Marathi"),
    ("मला दोन टप्प्यांत फी भरायची आहे, परवानगी मिळेल का?", "INSTALLMENT", "Marathi"),
    ("फी च्या हप्त्यांचे वेळापत्रक काय आहे?", "INSTALLMENT", "Marathi"),
    ("आर्थिक अडचणींमुळे फी तीन हप्त्यात भरता येईल का?", "INSTALLMENT", "Marathi"),

    # ══════════════════════════════════════════════════════════════════════════
    # 7. SCHOLARSHIP
    # ══════════════════════════════════════════════════════════════════════════
    # English
    ("How does scholarship affect my total fee amount?", "SCHOLARSHIP", "English"),
    ("Has my government scholarship concession been applied to my fees?", "SCHOLARSHIP", "English"),
    ("What is the fee concession for OBC/SC/ST categories?", "SCHOLARSHIP", "English"),
    ("How much fee waiver do I get under the merit scholarship?", "SCHOLARSHIP", "English"),
    ("Why is my scholarship discount not reflecting in my fee balance?", "SCHOLARSHIP", "English"),
    ("What are the eligibility criteria for EBC fee concession?", "SCHOLARSHIP", "English"),
    ("How to link MahaDBT scholarship with college fee portal?", "SCHOLARSHIP", "English"),
    ("Will my scholarship amount be directly adjusted against my tuition fee?", "SCHOLARSHIP", "English"),
    ("How much deduction do TFWS scheme students get on tuition fee?", "SCHOLARSHIP", "English"),
    ("I have received 15000 scholarship, why does portal show 25000 pending?", "SCHOLARSHIP", "English"),
    ("Where do I submit the scholarship application form in college?", "SCHOLARSHIP", "English"),
    ("Is there any fee reduction for female students?", "SCHOLARSHIP", "English"),
    ("Can I get fee reimbursement from government schemes?", "SCHOLARSHIP", "English"),
    ("What documents are needed for scholarship fee waiver?", "SCHOLARSHIP", "English"),
    ("Can sports quota students get fee concessions?", "SCHOLARSHIP", "English"),
    ("Does fee concession apply to hostel charges as well?", "SCHOLARSHIP", "English"),
    # Hindi
    ("स्कॉलरशिप से मेरी फीस में कितनी छूट मिलेगी?", "SCHOLARSHIP", "Hindi"),
    ("क्या मेरी छात्रवृत्ति की राशि फीस में से कम हो गई है?", "SCHOLARSHIP", "Hindi"),
    ("ओबीसी और एससी/एसटी छात्रों के लिए फीस में कितनी रियायत है?", "SCHOLARSHIP", "Hindi"),
    ("मेरिट स्कॉलरशिप मिलने पर कितनी फीस माफ होती है?", "SCHOLARSHIP", "Hindi"),
    ("महाडीबीटी स्कॉलरशिप का पैसा फीस में कब एडजस्ट होगा?", "SCHOLARSHIP", "Hindi"),
    ("ईबीसी योजना के तहत फीस में कितनी छूट मिलती है?", "SCHOLARSHIP", "Hindi"),
    ("मेरी 10000 की स्कॉलरशिप पोर्टल पर क्यों नहीं दिख रही?", "SCHOLARSHIP", "Hindi"),
    ("टीएफडब्ल्यूएस कोटे में ट्यूशन फीस पूरी माफ होती है क्या?", "SCHOLARSHIP", "Hindi"),
    ("स्कॉलरशिप का फॉर्म भरने के लिए कौन से दस्तावेज चाहिए?", "SCHOLARSHIP", "Hindi"),
    ("क्या छात्रा को फीस में कोई विशेष छूट मिलती है?", "SCHOLARSHIP", "Hindi"),
    ("छात्रवृत्ति मिलने के बाद बची हुई फीस कितनी भरनी होगी?", "SCHOLARSHIP", "Hindi"),
    ("कॉलेज फीस में स्कॉलरशिप डिस्काउंट कैसे लागू होता है?", "SCHOLARSHIP", "Hindi"),
    ("क्या अल्पसंख्यक स्कॉलरशिप से फीस कम हो सकती है?", "SCHOLARSHIP", "Hindi"),
    # Marathi
    ("शिष्यवृत्तीमुळे माझ्या फी मध्ये किती सूट मिळेल?", "SCHOLARSHIP", "Marathi"),
    ("माझी शासकीय शिष्यवृत्ती फी मध्ये वजा झाली आहे का?", "SCHOLARSHIP", "Marathi"),
    ("ओबीसी आणि एससी प्रवर्गासाठी फी मध्ये किती सवलत आहे?", "SCHOLARSHIP", "Marathi"),
    ("महाडीबीटी स्कॉलरशिप जमा झाल्यानंतर किती फी भरावी लागेल?", "SCHOLARSHIP", "Marathi"),
    ("ईबीसी सवलतीनुसार किती फी माफ होते?", "SCHOLARSHIP", "Marathi"),
    ("माझ्या फी बिलात शिष्यवृत्तीची रक्कम का दिसत नाही?", "SCHOLARSHIP", "Marathi"),
    ("टीएफडब्ल्यूएस अंतर्गत ट्यूशन फी पूर्णपणे माफ असते का?", "SCHOLARSHIP", "Marathi"),
    ("शिष्यवृत्ती मंजुरीचे प्रमाणपत्र कुठे जमा करायचे?", "SCHOLARSHIP", "Marathi"),
    ("१०,००० रुपयांची स्कॉलरशिप वजा झाल्यावर बाकी फी किती?", "SCHOLARSHIP", "Marathi"),
    ("गुणवत्ता शिष्यवृत्तीच्या नियमांनुसार फी सवलत किती मिळते?", "SCHOLARSHIP", "Marathi"),
    ("मुलींसाठी फी मध्ये काही विशेष सवलत आहे का?", "SCHOLARSHIP", "Marathi"),
    ("अनाथ किंवा दिव्यांग विद्यार्थ्यांना फी मध्ये सवलत आहे का?", "SCHOLARSHIP", "Marathi"),

    # ══════════════════════════════════════════════════════════════════════════
    # 8. REFUND
    # ══════════════════════════════════════════════════════════════════════════
    # English
    ("How can I apply for a fee refund?", "REFUND", "English"),
    ("What is the college fee refund policy if I cancel my admission?", "REFUND", "English"),
    ("I accidentally paid twice, how will I get my money back?", "REFUND", "English"),
    ("How many days does it take to process a fee refund?", "REFUND", "English"),
    ("Will my caution money and security deposit be refunded after graduation?", "REFUND", "English"),
    ("How do I get a refund for excess fee paid?", "REFUND", "English"),
    ("What percentage of tuition fee is refundable after 15 days of college start?", "REFUND", "English"),
    ("Check the status of my fee refund application REF-2026.", "REFUND", "English"),
    ("Can I get a refund of hostel security deposit?", "REFUND", "English"),
    ("Double payment was deducted from my account for exam fees, please refund.", "REFUND", "English"),
    ("Whom should I contact for refund of overpaid fees?", "REFUND", "English"),
    ("Is library deposit refundable when leaving college?", "REFUND", "English"),
    ("What is the cancellation and refund rule as per UGC guidelines?", "REFUND", "English"),
    ("Has my refund request of 25000 been approved?", "REFUND", "English"),
    ("I want to initiate cancellation of registration and claim refund.", "REFUND", "English"),
    ("Where do I submit bank details for fee refund credit?", "REFUND", "English"),
    # Hindi
    ("फीस रिफंड के लिए कैसे आवेदन करें?", "REFUND", "Hindi"),
    ("एडमिशन कैंसिल करने पर फीस वापस मिलेगी क्या?", "REFUND", "Hindi"),
    ("गलती से दो बार फीस कट गई, पैसे वापस कैसे मिलेंगे?", "REFUND", "Hindi"),
    ("फीस वापसी में कितने दिन का समय लगता है?", "REFUND", "Hindi"),
    ("क्या कॉलेज पूरा होने पर कॉशन मनी रिफंड होती है?", "REFUND", "Hindi"),
    ("ज्यादा भरी हुई फीस को वापस पाने का क्या तरीका है?", "REFUND", "Hindi"),
    ("मेरे रिफंड आवेदन की वर्तमान स्थिति क्या है?", "REFUND", "Hindi"),
    ("हॉस्टल सिक्योरिटी डिपॉजिट कब वापस किया जाता है?", "REFUND", "Hindi"),
    ("यूजीसी नियमों के मुताबिक कितनी फीस रिफंड होगी?", "REFUND", "Hindi"),
    ("अकाउंट्स ऑफिस से रिफंड चेक कब मिलेगा?", "REFUND", "Hindi"),
    ("क्या परीक्षा फीस रिफंड हो सकती है?", "REFUND", "Hindi"),
    ("डबल पेमेंट का पैसा मेरे खाते में कब तक आएगा?", "REFUND", "Hindi"),
    ("एडमिशन विड्रॉ करने पर कितने प्रतिशत पैसा कटता है?", "REFUND", "Hindi"),
    # Marathi
    ("फी परतावा (रिफंड) मिळवण्यासाठी अर्ज कसा करावा?", "REFUND", "Marathi"),
    ("प्रवेश रद्द केल्यास भरलेली फी परत मिळते का?", "REFUND", "Marathi"),
    ("माझ्याकडून दोनदा फी कापली गेली, पैसे परत कसे मिळतील?", "REFUND", "Marathi"),
    ("फी रिफंड होण्यासाठी किती दिवस लागतात?", "REFUND", "Marathi"),
    ("कॉलेज संपल्यानंतर डिपॉझिटचे पैसे परत मिळतील का?", "REFUND", "Marathi"),
    ("जास्तीची भरलेली फी परत मिळण्याची प्रक्रिया काय आहे?", "REFUND", "Marathi"),
    ("माझ्या रिफंड अर्जाची सध्याची स्थिती काय आहे?", "REFUND", "Marathi"),
    ("हॉस्टेल अनामत रक्कम केव्हा परत मिळते?", "REFUND", "Marathi"),
    ("दुहेरी पेमेंट झालेल्या पैशांचा परतावा कधी जमा होईल?", "REFUND", "Marathi"),
    ("प्रवेश रद्द करताना किती टक्के फी कापून घेतली जाते?", "REFUND", "Marathi"),
    ("वाचनालय अनामत रक्कम परत मिळवण्यासाठी काय करावे लागेल?", "REFUND", "Marathi"),
    ("परतावा थेट बँक खात्यात एनईएफटी द्वारे जमा होतो का?", "REFUND", "Marathi"),

    # ══════════════════════════════════════════════════════════════════════════
    # 9. RECEIPT
    # ══════════════════════════════════════════════════════════════════════════
    # English
    ("How do I download my fee receipt?", "RECEIPT", "English"),
    ("Where can I get the payment receipt for semester 5?", "RECEIPT", "English"),
    ("I need an official stamped fee receipt for my education loan.", "RECEIPT", "English"),
    ("Can you send my fee receipt to my registered email address?", "RECEIPT", "English"),
    ("I cannot find the receipt download button on my student portal.", "RECEIPT", "English"),
    ("How can I print my previous semester fee receipt?", "RECEIPT", "English"),
    ("Does the downloaded receipt contain the college seal and signature?", "RECEIPT", "English"),
    ("Generate duplicate fee receipt for transaction TXN984210482.", "RECEIPT", "English"),
    ("Can I get an income tax 80E fee certificate/receipt from college?", "RECEIPT", "English"),
    ("Where to collect the physical fee receipt on campus?", "RECEIPT", "English"),
    ("I need the payment invoice for tuition fees paid yesterday.", "RECEIPT", "English"),
    ("Please provide the receipt for my hostel fee payment.", "RECEIPT", "English"),
    ("Download fee receipt PDF for academic year 2025-26.", "RECEIPT", "English"),
    ("Show my latest fee receipt on the screen.", "RECEIPT", "English"),
    ("Can I get the receipt for the 50000 rupees tuition deposit?", "RECEIPT", "English"),
    ("Where is the transaction acknowledgment receipt stored?", "RECEIPT", "English"),
    # Hindi
    ("फीस की रसीद कैसे डाउनलोड करें?", "RECEIPT", "Hindi"),
    ("पांचवें सेमेस्टर की फीस रसीद कहां से मिलेगी?", "RECEIPT", "Hindi"),
    ("एजुकेशन लोन के लिए मुझे कॉलेज की मुहर लगी फीस रसीद चाहिए।", "RECEIPT", "Hindi"),
    ("क्या मेरी फीस की रसीद मेरी ईमेल आईडी पर भेजी जा सकती है?", "RECEIPT", "Hindi"),
    ("पोर्टल पर रसीद डाउनलोड करने का ऑप्शन नहीं दिख रहा है।", "RECEIPT", "Hindi"),
    ("पुराने सेमेस्टर की फीस रसीद कैसे प्रिंट करें?", "RECEIPT", "Hindi"),
    ("क्या इस डिजिटल रसीद को बैंक में लोन के लिए दिखा सकते हैं?", "RECEIPT", "Hindi"),
    ("मेरी हालिया पेमेंट की इनवॉइस चाहिए।", "RECEIPT", "Hindi"),
    ("फीस जमा करने की पक्की रसीद कहां से प्राप्त होगी?", "RECEIPT", "Hindi"),
    ("डुप्लीकेट फीस रसीद प्राप्त करने का क्या नियम है?", "RECEIPT", "Hindi"),
    ("हॉस्टल फीस की रसीद कैसे निकालें?", "RECEIPT", "Hindi"),
    ("टैक्स छूट के लिए फीस सर्टिफिकेट कैसे मिलेगा?", "RECEIPT", "Hindi"),
    ("क्या रसीद पर प्रिंसिपल के हस्ताक्षर जरूरी हैं?", "RECEIPT", "Hindi"),
    # Marathi
    ("फी भरल्याची पावती कशी डाउनलोड करावी?", "RECEIPT", "Marathi"),
    ("पाचव्या सत्राची फी पावती कुठून मिळेल?", "RECEIPT", "Marathi"),
    ("शैक्षणिक कर्जासाठी (Education Loan) सही-शिक्क्याची फी पावती हवी आहे.", "RECEIPT", "Marathi"),
    ("माझ्या ईमेलवर फी ची पावती पाठवता येईल का?", "RECEIPT", "Marathi"),
    ("मागील सेमिस्टरची फी पावती कशी प्रिंट करायची?", "RECEIPT", "Marathi"),
    ("पोर्टलवरून फी पावती ची पीडीएफ कशी डाऊनलोड करावी?", "RECEIPT", "Marathi"),
    ("मूळ फी पावती गहाळ झाल्यास डुप्लिकेट पावती मिळेल का?", "RECEIPT", "Marathi"),
    ("हॉस्टेल फी भरल्याची पावती कुठे मिळते?", "RECEIPT", "Marathi"),
    ("इन्कम टॅक्स सवलतीसाठी फी प्रमाणपत्र कुठे मिळेल?", "RECEIPT", "Marathi"),
    ("माझ्या शेवटच्या व्यवहाराची पावती मला हवी आहे.", "RECEIPT", "Marathi"),
    ("कॉलेज काउंटरवरून प्रत्यक्ष पावती कधी मिळेल?", "RECEIPT", "Marathi"),
    ("ऑनलाइन पेमेंट पावती अधिकृत मानली जाते का?", "RECEIPT", "Marathi"),

    # ══════════════════════════════════════════════════════════════════════════
    # 10. OTHER_FEE_QUERY
    # ══════════════════════════════════════════════════════════════════════════
    # English
    ("What are the working hours of the college accounts office?", "OTHER_FEE_QUERY", "English"),
    ("Can I pay my fees using a credit card or debit card?", "OTHER_FEE_QUERY", "English"),
    ("Is cash payment accepted at the college fee counter?", "OTHER_FEE_QUERY", "English"),
    ("How do I contact the finance officer regarding fee issues?", "OTHER_FEE_QUERY", "English"),
    ("Are there any extra charges for online payment gateways?", "OTHER_FEE_QUERY", "English"),
    ("What payment modes are supported: UPI, NEFT, RTGS or DD?", "OTHER_FEE_QUERY", "English"),
    ("In whose name should the demand draft (DD) be drawn for fees?", "OTHER_FEE_QUERY", "English"),
    ("Can my parents pay the fees directly from their bank account?", "OTHER_FEE_QUERY", "English"),
    ("Whom to reach if fee portal shows a technical server error?", "OTHER_FEE_QUERY", "English"),
    ("Is there an education loan assistance desk in the college?", "OTHER_FEE_QUERY", "English"),
    ("Where is the student fee accounts department located on campus?", "OTHER_FEE_QUERY", "English"),
    ("What are the bank account details of the college for NEFT transfer?", "OTHER_FEE_QUERY", "English"),
    ("Can I get a bonafide certificate for fee reimbursement from father's office?", "OTHER_FEE_QUERY", "English"),
    ("How to update my category details in the fee portal?", "OTHER_FEE_QUERY", "English"),
    ("Do I need to pay repeat examination charges if reappearing for a subject?", "OTHER_FEE_QUERY", "English"),
    ("What is the helpline number for student fee queries?", "OTHER_FEE_QUERY", "English"),
    # Hindi
    ("कॉलेज अकाउंट्स ऑफिस का समय क्या है?", "OTHER_FEE_QUERY", "Hindi"),
    ("क्या कॉलेज में कैश या चेक से फीस भरी जा सकती है?", "OTHER_FEE_QUERY", "Hindi"),
    ("फीस के लिए डिमांड ड्राफ्ट किसके नाम पर बनाना होगा?", "OTHER_FEE_QUERY", "Hindi"),
    ("ऑनलाइन पेमेंट करने पर कितना गेटवे चार्ज लगता है?", "OTHER_FEE_QUERY", "Hindi"),
    ("फीस संबंधी समस्याओं के लिए किससे संपर्क करना चाहिए?", "OTHER_FEE_QUERY", "Hindi"),
    ("क्या क्रेडिट कार्ड से फीस भरने पर ईएमआई का विकल्प है?", "OTHER_FEE_QUERY", "Hindi"),
    ("एनईएफटी ट्रांसफर के लिए कॉलेज का बैंक खाता नंबर और आईएफएससी क्या है?", "OTHER_FEE_QUERY", "Hindi"),
    ("क्या मेरे माता-पिता अपने अकाउंट से सीधे फीस ट्रांसफर कर सकते हैं?", "OTHER_FEE_QUERY", "Hindi"),
    ("फीस पोर्टल पर एरर आ रहा है, टेक्निकल टीम से कैसे बात करें?", "OTHER_FEE_QUERY", "Hindi"),
    ("एजुकेशन लोन के लिए कॉलेज से कौन से कागजात मिलेंगे?", "OTHER_FEE_QUERY", "Hindi"),
    ("अकाउंट्स काउंटर कॉलेज में किस बिल्डिंग में है?", "OTHER_FEE_QUERY", "Hindi"),
    ("री-इवैल्यूएशन और बैक फॉर्म की फीस कितनी लगती है?", "OTHER_FEE_QUERY", "Hindi"),
    ("फीस काउंटर शनिवार को खुला रहता है क्या?", "OTHER_FEE_QUERY", "Hindi"),
    # Marathi
    ("कॉलेजच्या फी विभागाचे कामाचे तास कोणते आहेत?", "OTHER_FEE_QUERY", "Marathi"),
    ("फी भरण्यासाठी डिमांड ड्राफ्ट (DD) कोणाच्या नावावर काढायचा?", "OTHER_FEE_QUERY", "Marathi"),
    ("कॉलेज काउंटरवर रोख (Cash) रक्कम स्वीकारली जाते का?", "OTHER_FEE_QUERY", "Marathi"),
    ("नेट बँकिंग किंवा युपीआय व्यतिरिक्त कोणते पर्याय उपलब्ध आहेत?", "OTHER_FEE_QUERY", "Marathi"),
    ("फी बाबत तक्रार असल्यास कोणाला भेटावे लागते?", "OTHER_FEE_QUERY", "Marathi"),
    ("एनईएफटी (NEFT) साठी कॉलेजचा बँक खाते क्रमांक आणि IFSC कोड काय आहे?", "OTHER_FEE_QUERY", "Marathi"),
    ("क्रेडिट कार्डने फी भरताना ईएमआय सुविधा मिळते का?", "OTHER_FEE_QUERY", "Marathi"),
    ("पालकांच्या बँक खात्यातून थेट फी भरता येईल का?", "OTHER_FEE_QUERY", "Marathi"),
    ("फी पोर्टलवर तांत्रिक अडचण आल्यास कोणाशी संपर्क करावा?", "OTHER_FEE_QUERY", "Marathi"),
    ("शैक्षणिक कर्जाच्या मदतीसाठी कॉलेजमध्ये स्वतंत्र कक्ष आहे का?", "OTHER_FEE_QUERY", "Marathi"),
    ("पुनर्मूल्यांकन (Revaluation) फी किती आकारली जाते?", "OTHER_FEE_QUERY", "Marathi"),
    ("फी विभागाचा संपर्क क्रमांक आणि ईमेल काय आहे?", "OTHER_FEE_QUERY", "Marathi"),
]

def generate():
    output_dir = os.path.join(os.path.dirname(__file__), "dataset")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "fees_queries.csv")

    seen = set()
    cleaned_data = []

    for text, intent, lang in DATA:
        normalized_text = text.strip()
        if normalized_text in seen:
            print(f"Skipping duplicate: {normalized_text}")
            continue
        seen.add(normalized_text)
        cleaned_data.append((normalized_text, intent, lang))

    with open(output_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "intent", "language"])
        for row in cleaned_data:
            writer.writerow(row)

    print(f"✅ Generated {len(cleaned_data)} queries in {output_file}")

    # Summary
    from collections import Counter
    intents = Counter(r[1] for r in cleaned_data)
    languages = Counter(r[2] for r in cleaned_data)
    print("\nIntents breakdown:")
    for k, v in sorted(intents.items()):
        print(f"  {k}: {v}")
    print("\nLanguages breakdown:")
    for k, v in sorted(languages.items()):
        print(f"  {k}: {v}")

if __name__ == "__main__":
    generate()

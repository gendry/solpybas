from zebra import zebra

def print_lab(label,printer):
	label = label
	z = zebra([])
	p = z.getqueues()
	#print p                                      #This will return a list of printers installed on your computer. 
	z.setqueue(printer)  #Set the default printer to your new ZPL printer
	z.output(label)                                  #Have fun sending data to your printer.It's as easy as it can get. :)
from flask import render_template, request

from app import create_app

app = create_app()

# <editor-fold desc="Error handlers">

@app.errorhandler(404)
def page_not_found(e):
	url = request.path
	return render_template('error.html', title='404', functionality=url, message='Page not found'), 404
# </editor-fold>

if __name__ == '__main__':
	app.run(debug=True, port=5000, host='0.0.0.0')

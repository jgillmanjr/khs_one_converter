from io import BytesIO
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
import oneconverter
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024  # 1 Meg
# 'process_fxp', 'process_au', 'process_re', 'process_fxb']
format_dict = {
    'fxp': ('process_fxp', 'return_fxp_data', 'fxp'),
    'aup': ('process_au', 'return_au_data', 'aupreset'),
    'res': ('process_re', 'return_reason_data', 'repatch'),
    'fxb': ('process_fxb', 'put_something_here', 'fxb'),
}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/convert', methods=['POST'])
def convert():
    from_fmt = request.form['from_fmt']
    to_fmt = request.form['to_fmt']
    parse_method = format_dict[from_fmt][0]
    export_method = format_dict[to_fmt][1]
    uploaded_preset = request.files['preset_file']
    preset_file_data = uploaded_preset.read()
    upload_file_name = secure_filename(uploaded_preset.filename)

    if parse_method != 'process_fxb':
        parsed_preset: oneconverter.preset.Preset = getattr(oneconverter, parse_method)(preset_file_data,
                                                                                        file_name=upload_file_name)
        parsed_preset_name = f'{parsed_preset.name}.{format_dict[to_fmt][2]}'
        converted_data_stream = BytesIO(getattr(parsed_preset, export_method)())

        return send_file(converted_data_stream, as_attachment=True, attachment_filename=parsed_preset_name)

    return 'Something happened. Sorry :( Hit us up on Discord.'


if __name__ == '__main__':
    app.run()

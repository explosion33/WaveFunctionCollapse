from app import app

def main():
    app.run(host="0.0.0.0", port=app.config["PORT"])

if __name__ == '__main__':
    main()
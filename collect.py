import glob


def main():
    with open('output.txt', 'w', encoding='utf-8') as outfile:
        # Собираем все .php и .css файлы
        for filename in glob.glob('*.php') + glob.glob('*.css'):
            # Записываем название файла
            outfile.write(f"\n{'=' * 20} {filename} {'=' * 20}\n\n")

            try:
                # Читаем содержимое файла
                with open(filename, 'r', encoding='utf-8') as infile:
                    content = infile.read()
                    # Записываем содержимое в выходной файл
                    outfile.write(content)
                    outfile.write('\n\n')
            except Exception as e:
                # Обработка ошибок чтения файла
                outfile.write(f"⚠️ Ошибка чтения файла {filename}: {str(e)}\n\n")
                print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()

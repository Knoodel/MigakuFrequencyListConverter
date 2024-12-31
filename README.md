# Migaku Frequency List Converter

Script that converts Yomichan frequency lists to Migaku format

## Basic Usage

1. Clone the repository

```bash
git clone https://github.com/Knoodel/MigakuFrequencyListConverter.git
```

2. Install the necessary libraries

```bash
cd MigakuFrequencyListConverter
pip install -r requirements.txt
```

3. In the `MigakuFrequencyListConverter` directory, create another directory called `dicts` and put Yomichan frequency lists inside
4. Run the script

```bash
python converter.py
```

5. Converted frequency list will appear inside a directory called `output`

## Supported Languages

The program was created for Japanese, so I can't guarantee it working for other languages.

## Known Limitations

1. Migaku frequency ratings have to be in ascending order, meaning lists that don't follow that order will be adjusted to the format. This makes it impossible to convert lists such as JLPT ratings (1-5).
2. Yomichan supports a property called "displayValue", meaning that while the actual frequency rating will be converted, it might not appear the same way as in Yomichan. For example `{"value":103,"displayValue":"100-200"}` will appear as `103`, not `100-200`.
3. [Homographs](https://legacy.migaku.io/tools-guides/migaku-dictionary/manual/#frequency-list-format)

document.addEventListener("DOMContentLoaded", function () {
    const nameField = document.querySelector("#id_name");
    const slugField = document.querySelector("#id_slug");

    if (nameField && slugField) {
        nameField.addEventListener("input", function () {
            this.value = this.value.replace(/[^a-zA-Zа-яА-Я0-9 _-]/g, "");

            let slug = transliterate(nameField.value)
                .toLowerCase()
                .trim()
                .replace(/\s+/g, "-");

            slugField.value = slug;
        });
    }

    function transliterate(text) {
        const ru = {
            "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo", "ж": "zh",
            "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o",
            "п": "p", "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f", "х": "kh", "ц": "ts",
            "ч": "ch", "ш": "sh", "щ": "shch", "ы": "y", "э": "e", "ю": "yu", "я": "ya",
            "ъ": "_", "ь": "_"
        };

        return text.split('').map(char => {
            let lowerChar = char.toLowerCase();
            return ru[lowerChar] || lowerChar;
        }).join('');
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const usernameField = document.querySelector("#id_username");
    const slugField = document.querySelector("#id_slug");

    if (usernameField && slugField) {
        usernameField.addEventListener("input", function () {
            let slug = transliterate(usernameField.value)
                .toLowerCase()
                .trim()
                .replace(/@/g, "-at-")  // Заменяем @ → "-at-"
                .replace(/\+/g, "-plus-")  // Заменяем + → "-plus-"
                .replace(/\./g, "-dot-")  // Заменяем . → "-dot-"

            slugField.value = slug;
        });
    }

    function transliterate(text) {
        const ru = {
            "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo", "ж": "zh",
            "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o",
            "п": "p", "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f", "х": "kh", "ц": "ts",
            "ч": "ch", "ш": "sh", "щ": "shch", "ы": "y", "э": "e", "ю": "yu", "я": "ya",
            "ъ": "", "ь": ""
        };

        return text.split('').map(char => {
            let lowerChar = char.toLowerCase();
            return ru[lowerChar] || lowerChar;
        }).join('');
    }
});

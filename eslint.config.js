import js from "@eslint/js";
import vue from "eslint-plugin-vue";
import tsParser from "@typescript-eslint/parser";
import globals from "globals";

export default [
    {
        ignores: ["node_modules/**", "dist/**", "coverage/**", "venv/**"],
    },
    {
        files: ["**/*.{js,mjs,cjs,ts}"],
        languageOptions: {
            parser: tsParser,
        },
    },
    js.configs.recommended,
    ...vue.configs["flat/recommended"],
    {
        files: ["**/*.{js,mjs,cjs,ts,vue}"],
        languageOptions: {
            ecmaVersion: "latest",
            sourceType: "module",
            parserOptions: {
                parser: tsParser,
            },
            globals: {
                ...globals.browser,
                ...globals.node,
            },
        },
        rules: {
            indent: ["error", 4, { SwitchCase: 1 }],
            "vue/script-indent": ["error", 4, { baseIndent: 0, switchCase: 1 }],
            "vue/html-indent": ["error", 4, { baseIndent: 0, attribute: 1, closeBracket: 0 }],
            "vue/html-self-closing": [
                "error",
                {
                    html: {
                        void: "any",
                        normal: "any",
                        component: "any",
                    },
                    svg: "any",
                    math: "any",
                },
            ],
            "vue/max-attributes-per-line": [
                "error",
                {
                    singleline: {
                        max: 8,
                    },
                    multiline: {
                        max: 1,
                    },
                },
            ],
        },
    },
    {
        files: ["testing/frontend/**/*.{js,mjs,cjs,ts}"],
        languageOptions: {
            globals: {
                ...globals.node,
                vi: "readonly",
                describe: "readonly",
                it: "readonly",
                expect: "readonly",
                beforeEach: "readonly",
                afterEach: "readonly",
            },
        },
    },
];

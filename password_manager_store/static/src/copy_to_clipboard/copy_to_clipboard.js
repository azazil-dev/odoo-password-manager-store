/** @odoo-module **/
/**
 * Client action: password_manager_store.copy_to_clipboard
 *
 * Copies the `params.text` value to the clipboard and shows a brief toast
 * notification. Registered as an Odoo 18 client action using the registry.
 *
 * Usage (from Python server action):
 *   return {
 *       'type': 'ir.actions.client',
 *       'tag': 'password_manager_store.copy_to_clipboard',
 *       'params': {'text': plaintext},
 *   }
 */

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";

/**
 * Copies text to clipboard using the modern Clipboard API when available,
 * with a fallback to the legacy execCommand approach for HTTP contexts.
 *
 * @param {string} text
 * @returns {Promise<boolean>} true on success
 */
async function copyTextToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (_e) {
            // Fall through to legacy method
        }
    }
    // Legacy fallback (works in insecure HTTP contexts)
    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.style.position = "fixed";
    textarea.style.opacity = "0";
    document.body.appendChild(textarea);
    textarea.focus();
    textarea.select();
    let success = false;
    try {
        success = document.execCommand("copy");
    } finally {
        document.body.removeChild(textarea);
    }
    return success;
}

/**
 * The client action handler receives the standard action env object from
 * Odoo's action service. `action.params.text` holds the plaintext to copy.
 */
registry.category("actions").add(
    "password_manager_store.copy_to_clipboard",
    async (env, action) => {
        const text = action.params && action.params.text;
        if (!text) {
            env.services.notification.add(_t("Nothing to copy."), {
                type: "warning",
            });
            return;
        }
        const success = await copyTextToClipboard(text);
        if (success) {
            env.services.notification.add(_t("Copied to clipboard."), {
                type: "success",
            });
        } else {
            env.services.notification.add(
                _t("Could not copy to clipboard. Please copy manually."),
                { type: "warning" }
            );
        }
    }
);

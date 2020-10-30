import i18n

LANGS_DIR = './config/lang'
i18n.set('locale', 'jp')
i18n.set('fallback', 'fr')
i18n.set('file_format', 'json')
i18n.set('skip_locale_root_data', True)
i18n.load_path.append(LANGS_DIR)

print(i18n.t('blender.tresorio-logout'))

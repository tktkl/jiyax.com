function chooseJiyaxLanguage(browserLanguage, savedLanguage, requestedLanguage) {
  for (const language of [requestedLanguage, savedLanguage]) {
    if (language === 'zh' || language === 'en') return language;
  }
  return /^zh(?:[-_]|$)/i.test(browserLanguage || '') ? 'zh' : 'en';
}

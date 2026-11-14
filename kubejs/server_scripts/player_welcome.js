PlayerEvents.loggedIn(event => {
  const d = event.player.persistentData
  if (!d.getBoolean('myneoforge_chronicles_04')) {
    d.putBoolean('myneoforge_chronicles_04', true)
    event.player.tell('§6[Chronicles] §f24 illustrated chapters are available in FTB Quests!')
  }
})

PlayerEvents.loggedIn(event => {
  const data = event.player.persistentData
  if (!data.getBoolean('myneoforge_welcome')) {
    data.putBoolean('myneoforge_welcome', true)
    event.player.tell('§6[Chronicles] §fOpen FTB Quests in your inventory. 14 chapters await!')
  }
})

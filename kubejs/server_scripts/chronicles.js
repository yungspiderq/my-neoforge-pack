// Generated, requires FTB XMod Compat 21.1.11 and KubeJS.

FTBQuestsEvents.customReward('7400000100000395', event => {
  const p = event.player
  p.give('4x minecraft:iron_ingot')
  p.persistentData.putBoolean('myneoforge_awakening', true)
  p.tell('§6[Chronicles] §fThe First Spark — complete!')
})

FTBQuestsEvents.customReward('7400000200000395', event => {
  const p = event.player
  p.give('2x minecraft:emerald')
  p.persistentData.putBoolean('myneoforge_homestead', true)
  p.tell('§6[Chronicles] §fThe Living Homestead — complete!')
})

FTBQuestsEvents.customReward('7400000300000395', event => {
  const p = event.player
  p.give('6x minecraft:golden_carrot')
  p.persistentData.putBoolean('myneoforge_mines', true)
  p.tell('§6[Chronicles] §fBeneath the Stone — complete!')
})

FTBQuestsEvents.customReward('7400000400000395', event => {
  const p = event.player
  p.give('8x minecraft:redstone')
  p.persistentData.putBoolean('myneoforge_fields', true)
  p.tell('§6[Chronicles] §fHarvest and Hearth — complete!')
})

FTBQuestsEvents.customReward('7400000500000395', event => {
  const p = event.player
  p.give('4x minecraft:iron_ingot')
  p.persistentData.putBoolean('myneoforge_builder', true)
  p.tell('§6[Chronicles] §fCity of One — complete!')
})

FTBQuestsEvents.customReward('7400000600000395', event => {
  const p = event.player
  p.give('2x minecraft:emerald')
  p.persistentData.putBoolean('myneoforge_wilderness', true)
  p.tell('§6[Chronicles] §fThe Wild Compass — complete!')
})

FTBQuestsEvents.customTask('7300000600000013', event => {
  event.maxProgress = 3
  event.setCheckTimer(100)
  event.setCheck((task, player) => {
    if (player.level.thundering) task.progress++
  })
})

FTBQuestsEvents.customReward('7400000700000395', event => {
  const p = event.player
  p.give('6x minecraft:golden_carrot')
  p.persistentData.putBoolean('myneoforge_redstone', true)
  p.tell('§6[Chronicles] §fRedstone Awakening — complete!')
})

FTBQuestsEvents.customReward('7400000800000395', event => {
  const p = event.player
  p.give('8x minecraft:redstone')
  p.persistentData.putBoolean('myneoforge_ocean', true)
  p.tell('§6[Chronicles] §fThe Deep Atlas — complete!')
})

FTBQuestsEvents.customReward('7400000900000395', event => {
  const p = event.player
  p.give('4x minecraft:iron_ingot')
  p.persistentData.putBoolean('myneoforge_alchemy', true)
  p.tell('§6[Chronicles] §fThe Arcane Workshop — complete!')
})

FTBQuestsEvents.customReward('7400000A00000395', event => {
  const p = event.player
  p.give('2x minecraft:emerald')
  p.persistentData.putBoolean('myneoforge_nether', true)
  p.tell('§6[Chronicles] §fThrough the Fire — complete!')
})

FTBQuestsEvents.customReward('7400000B00000395', event => {
  const p = event.player
  p.give('6x minecraft:golden_carrot')
  p.persistentData.putBoolean('myneoforge_end', true)
  p.tell('§6[Chronicles] §fBeyond the Horizon — complete!')
})

FTBQuestsEvents.customReward('7400000C00000395', event => {
  const p = event.player
  p.give('8x minecraft:redstone')
  p.persistentData.putBoolean('myneoforge_create_first', true)
  p.tell('§6[Chronicles] §fCreate: Foundations — complete!')
})

FTBQuestsEvents.customReward('7400000D00000395', event => {
  const p = event.player
  p.give('4x minecraft:iron_ingot')
  p.persistentData.putBoolean('myneoforge_create_motion', true)
  p.tell('§6[Chronicles] §fCreate: Moving Cities — complete!')
})

FTBQuestsEvents.customReward('7400000E00000395', event => {
  const p = event.player
  p.give('2x minecraft:emerald')
  p.persistentData.putBoolean('myneoforge_create_factory', true)
  p.tell('§6[Chronicles] §fCreate: The Grand Factory — complete!')
})

FTBQuestsEvents.customReward('7400000F0000039D', event => {
  const p = event.player
  p.give('6x minecraft:golden_carrot')
  p.persistentData.putBoolean('myneoforge_villages', true)
  p.tell('§6[Chronicles] §fVillage of Trades — complete!')
})

FTBQuestsEvents.customReward('740000100000039D', event => {
  const p = event.player
  p.give('8x minecraft:redstone')
  p.persistentData.putBoolean('myneoforge_archaeology', true)
  p.tell('§6[Chronicles] §fDust and Relics — complete!')
})

FTBQuestsEvents.customReward('740000110000039D', event => {
  const p = event.player
  p.give('4x minecraft:iron_ingot')
  p.persistentData.putBoolean('myneoforge_deep_dark', true)
  p.tell('§6[Chronicles] §fThe Silent Depths — complete!')
})

FTBQuestsEvents.customReward('740000120000039D', event => {
  const p = event.player
  p.give('2x minecraft:emerald')
  p.persistentData.putBoolean('myneoforge_explorers', true)
  p.tell('§6[Chronicles] §fAtlas of Horizons — complete!')
})

FTBQuestsEvents.customReward('740000130000039D', event => {
  const p = event.player
  p.give('6x minecraft:golden_carrot')
  p.persistentData.putBoolean('myneoforge_skyward', true)
  p.tell('§6[Chronicles] §fAbove the Clouds — complete!')
})

FTBQuestsEvents.customReward('740000140000039D', event => {
  const p = event.player
  p.give('8x minecraft:redstone')
  p.persistentData.putBoolean('myneoforge_create_logistics', true)
  p.tell('§6[Chronicles] §fCreate: Sorting Networks — complete!')
})

FTBQuestsEvents.customReward('740000150000039D', event => {
  const p = event.player
  p.give('4x minecraft:iron_ingot')
  p.persistentData.putBoolean('myneoforge_create_trains', true)
  p.tell('§6[Chronicles] §fCreate: Iron Roads — complete!')
})

FTBQuestsEvents.customReward('740000160000039D', event => {
  const p = event.player
  p.give('2x minecraft:emerald')
  p.persistentData.putBoolean('myneoforge_create_steam', true)
  p.tell('§6[Chronicles] §fCreate: Steam Age — complete!')
})

FTBQuestsEvents.customReward('740000170000039D', event => {
  const p = event.player
  p.give('6x minecraft:golden_carrot')
  p.persistentData.putBoolean('myneoforge_create_contraptions', true)
  p.tell('§6[Chronicles] §fCreate: Moving Worlds — complete!')
})

FTBQuestsEvents.customReward('740000180000039D', event => {
  const p = event.player
  p.give('8x minecraft:redstone')
  p.persistentData.putBoolean('myneoforge_create_mastery', true)
  p.tell('§6[Chronicles] §fCreate: The Masterworks — complete!')
})

FTBQuestsEvents.customTask('730000180000001B', event => {
  event.maxProgress = 1
  event.setCheckTimer(40)
  event.setCheck((task, player) => {
    const d = player.persistentData
    if (d.getBoolean('myneoforge_create_first') &&
        d.getBoolean('myneoforge_create_motion') &&
        d.getBoolean('myneoforge_create_factory')) task.progress = 1
  })
})

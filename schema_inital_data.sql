drop table user_data;
drop table snark;
drop table uptime;

SET timezone = 'America/New_York';
CREATE TABLE user_data (
   username text,
   room text,
   kind text,
   payload text,
   count integer,
   event_time TIMESTAMPTZ DEFAULT now()
);


CREATE TABLE snark (
   username text,
   kind text,
   rate integer,
   content text
);

CREATE TABLE DND (
   category text,
   id integer,
   content text
);

CREATE TABLE uptime(
   serial_id SERIAL,
   started TIMESTAMP DEFAULT now(),
   username text default 'torpedobot'
);



-- This part is untested.... Run at your own risk.
-- COPY public.dnd (category, id, content) FROM stdin;
-- organ 1  ankle
-- organ 2  arm
-- organ 3  arse
-- organ 4  bung
-- organ 5  calf
-- organ 6  ear
-- organ 7  elbow
-- organ 8  eye
-- organ 9  face
-- organ 10 foot
-- organ 11 forehead
-- organ 12 giblets
-- organ 13 groin
-- organ 14 head
-- organ 15 kidney
-- organ 16 knee
-- organ 17 leg
-- organ 18 lower back
-- organ 19 neck
-- organ 20 nipple
-- organ 21 shin
-- organ 22 shoulder
-- organ 23 skull
-- organ 24 solar plexus
-- organ 25 thigh
-- organ 26 throat
-- weapon   1  club
-- weapon   2  dagger
-- weapon   3  greatclub
-- weapon   4  handaxe
-- weapon   5  javelin
-- weapon   6  light hammer
-- weapon   7  mace
-- weapon   8  quarterstaff
-- weapon   9  sickle
-- weapon   10 spear
-- weapon   11 crossbow
-- weapon   12 sling
-- weapon   13 battle axe
-- weapon   14 glaive
-- weapon   15 great axe
-- weapon   16 great sword
-- weapon   17 halberd
-- weapon   18 lance
-- weapon   19 longsword
-- weapon   20 maul
-- weapon   21 morningstar
-- weapon   22 pike
-- weapon   23 rapier
-- weapon   24 scimitar
-- weapon   25 short sword
-- weapon   26 trident
-- weapon   27 war pick
-- weapon   28 warhammer
-- weapon   29 whip
-- weapon   30 blowgun
-- weapon   31 longbow
-- animal   1  snake
-- animal   2  honeybadger
-- animal   3  tardigrade
-- animal   4  hummingbird
-- animal   5  cheetah
-- animal   6  turtle
-- animal   7  camel
-- animal   8  bear
-- animal   9  gopher
-- animal   10 fox
-- Foe   1  Acolyte
-- Foe   2  Air Elemental
-- Foe   3  Ape
-- Foe   4  Archmage
-- Foe   5  Assassin
-- Foe   6  Awakened Tree
-- Foe   7  Axe Beak
-- Foe   8  Azer
-- Foe   9  Baboon
-- Foe   10 Badger
-- Foe   11 Balor
-- Foe   12 Bandit
-- Foe   13 Barbed Devil
-- Foe   14 Basilisk
-- Foe   15 Bat
-- Foe   16 Bearded Devil
-- Foe   17 Behir
-- Foe   18 Berserker
-- Foe   19 Black Bear
-- Foe   20 Black Pudding
-- Foe   21 Blink Dog
-- Foe   22 Blood Hawk
-- Foe   23 Boar
-- Foe   24 Bone Devil
-- Foe   25 Brown Bear
-- Foe   26 Bugbear
-- Foe   27 Bulette
-- Foe   28 Camel
-- Foe   29 Cat
-- Foe   30 Centaur
-- Foe   31 Chain Devil
-- Foe   32 Chimera
-- Foe   33 Chuul
-- Foe   34 Clay Golem
-- Foe   35 Cloaker
-- Foe   36 Cockatrice
-- Foe   37 Commoner
-- Foe   38 Constricfor Snake
-- Foe   39 Couatl
-- Foe   40 Crab
-- Foe   41 Crocodile
-- Foe   42 Cult Fanatic
-- Foe   43 Cultist
-- Foe   44 Darkmantle
-- Foe   45 Death Dog
-- Foe   46 Deep Gnome
-- Foe   47 Deer
-- Foe   48 Deva
-- Foe   49 Dire Wolf
-- Foe   50 Djinni
-- Foe   51 Doppelganger
-- Foe   52 Draft Horse
-- Foe   53 Dretch
-- Foe   54 Drider
-- Foe   55 Drow
-- Foe   56 Druid
-- Foe   57 Dryad
-- Foe   58 Duergar
-- Foe   59 Dust Mephit
-- Foe   60 Eagle
-- Foe   61 Earth Elemental
-- Foe   62 Efreeti
-- Foe   63 Elephant
-- Foe   64 Elk
-- Foe   65 Erinyes
-- Foe   66 Ettercap
-- Foe   67 Ettin
-- Foe   68 Fire Elemental
-- Foe   69 Flesh Golem
-- Foe   70 Flying Snake
-- Foe   71 Flying Sword
-- Foe   72 Frog
-- Foe   73 Gargoyle
-- Foe   74 Gelatinous Cube
-- Foe   75 Ghast
-- Foe   76 Ghost
-- Foe   77 Ghoul
-- Foe   78 Gibbering Mouther
-- Foe   79 Glabrezu
-- Foe   80 Gladiafor
-- Foe   81 Gnoll
-- Foe   82 Goat
-- Foe   83 Goblin
-- Foe   84 Gorgon
-- Foe   85 Gray Ooze
-- Foe   86 Green Hag
-- Foe   87 Grick
-- Foe   88 Greliffon
-- Foe   89 Grimlock
-- Foe   90 Guard
-- Foe   91 Guardian Naga
-- Foe   92 Gynosphinx
-- Foe   93 Harpy
-- Foe   94 Hawk
-- Foe   95 Hell Hound
-- Foe   96 Hezrou
-- Foe   97 Hippogreliff
-- Foe   98 Hobgoblin
-- Foe   99 Homunculus
-- Foe   100   Horned Devil
-- Foe   101   Hunter Shark
-- Foe   102   Hydra
-- Foe   103   Hyena
-- Foe   104   Ice Devil
-- Foe   105   Ice Mephit
-- Foe   106   Imp
-- Foe   107   Incubus
-- Foe   108   Invisible Stalker
-- Foe   109   Iron Golem
-- Foe   110   Jackal
-- Foe   111   Killer Whale
-- Foe   112   Knight
-- Foe   113   Kobold
-- Foe   114   Kraken
-- Foe   115   Lamia
-- Foe   116   Lemure
-- Foe   117   Lich
-- Foe   118   Lion
-- Foe   119   Lizard
-- Foe   120   Lizardfolk
-- Foe   121   Mage
-- Foe   122   Magma Mephit
-- Foe   123   Magmin
-- Foe   124   Mammoth
-- Foe   125   Manticore
-- Foe   126   Marilith
-- Foe   127   Masteliff
-- Foe   128   Medusa
-- Foe   129   Merfolk
-- Foe   130   Merrow
-- Foe   131   Mimic
-- Foe   132   Minotaur
-- Foe   133   Mule
-- Foe   134   Mummy
-- Foe   135   Nalfeshnee
-- Foe   136   Night Hag
-- Foe   137   Nightmare
-- Foe   138   Noble
-- Foe   139   Ochre Jelly
-- Foe   140   Octopus
-- Foe   141   Ogre
-- Foe   142   Ogre Zombie
-- Foe   143   Oni
-- Foe   144   Orc
-- Foe   145   Otyugh
-- Foe   146   Owl
-- Foe   147   Owlbear
-- Foe   148   Panther
-- Foe   149   Pegasus
-- Foe   150   Phase Spider
-- Foe   151   Pit Fiend
-- Foe   152   Planetar
-- Foe   153   Plesiosaurus
-- Foe   154   Poisonous Snake
-- Foe   155   Polar Bear
-- Foe   156   Pony
-- Foe   157   Priest
-- Foe   158   Pseudodragon
-- Foe   159   Purple Worm
-- Foe   160   Quasit
-- Foe   161   Quipper
-- Foe   162   Rakshasa
-- Foe   163   Rat
-- Foe   164   Raven
-- Foe   165   Reef Shark
-- Foe   166   Remorhaz
-- Foe   167   Rhinoceros
-- Foe   168   Riding Horse
-- Foe   169   Roc
-- Foe   170   Roper
-- Foe   171   Rug of Smothering
-- Foe   172   Rust Monster
-- Foe   173   Saber-Toothed Tiger
-- Foe   174   Sahuagin
-- Foe   175   Salamander
-- Foe   176   Satyr
-- Foe   177   Scorpion
-- Foe   178   Scout
-- Foe   179   Sea Hag
-- Foe   180   Sea Horse
-- Foe   181   Shadow
-- Foe   182   Shambling Mound
-- Foe   183   Shield Guardian
-- Foe   184   Shrieker
-- Foe   185   Skeleton
-- Foe   186   Solar
-- Foe   187   Specter
-- Foe   188   Spider
-- Foe   189   Spirit Naga
-- Foe   190   Sprite
-- Foe   191   Spy
-- Foe   192   Steam Mephit
-- Foe   193   Stirge
-- Foe   194   Stone Golem
-- Foe   195   Succubus
-- Foe   196   Swarm of Bats
-- Foe   197   Swarm of Beetles
-- Foe   198   Swarm of Centipedes
-- Foe   199   Swarm of Insects
-- Foe   200   Swarm of Poisonous Snakes
-- Foe   201   Swarm of Quippers
-- Foe   202   Swarm of Rats
-- Foe   203   Swarm of Ravens
-- Foe   204   Swarm of Spiders
-- Foe   205   Swarm of Wasps
-- Foe   206   Tarrasque
-- Foe   207   Thug
-- Foe   208   Tiger
-- Foe   209   Treant
-- Foe   210   Tribal Warrior
-- Foe   211   Triceratops
-- Foe   212   Troll
-- Foe   213   Tyrannosaurus Rex
-- Foe   214   Unicorn
-- Foe   215   Vampire
-- Foe   216   Vampire Spawn
-- Foe   217   Veteran
-- Foe   218   Violet Fungus
-- Foe   219   Vrock
-- Foe   220   Vulture
-- Foe   221   Warhorse
-- Foe   222   Warhorse Skeleton
-- Foe   223   Water Elemental
-- Foe   224   Weasel
-- Foe   225   Werebear
-- Foe   226   Werewolf
-- Foe   227   Will-o-Wisp
-- Foe   228   Winter Wolf
-- Foe   229   Wolf
-- Foe   230   Worg
-- Foe   231   Wraith
-- Foe   232   Wyvern
-- Foe   233   Zombie
-- Foe   234   Dragon
-- \.

# Things to add to scratchattach.editor (sbeditor v2)

## All

- [ ] Docstrings
- [x] Dealing with stuff from the backpack (it's in a weird format): This may require a whole separate module
- [ ] Getter functions (`@property`) instead of directly editing attrs (make them protected attrs)
- [ ] Check if whitespace chars break IDs
- [ ] Maybe blockchain should be renamed to 'script'
- [ ] Perhaps use sprites as blockchain wrappers due to their existing utility (loading of local globals etc)
- [ ] bs4 styled search function
- [ ] ScratchJR project parser (lol)
- [ ] Error checking (for when you need to specify sprite etc)
- [ ] Split json unpacking and the use of .from_json method so that it is easy to just extract json data (but not parse
  it)

## Project

- [x] Asset list
- [ ] Obfuscation
- [x] Detection for twconfig
- [x] Edit twconfig
- [ ] Find targets

## Block

### Finding blocks/attrs

- [x] Top level block (stack parent)
- [x] Previous chain
- [x] Attached chain
- [x] Complete chain
- [x] Block categories
- [x] Block shape attr aka stack type (Stack/hat/c-mouth/end/reporter/boolean detection)
- [x] `can_next` property
- [x] `is_input` property: Check if block is an input obscurer
- [x] `parent_input` property: Get input that this block obscures
- [x] `stack_tree` old 'subtree' property: Get the 'ast' of this blockchain (a 'tree' structure - well actually a list
  of lists)
- [x] `children` property - list of all blocks with this block as a parent except next block (any input obscurers)
- [x] Detection for turbowarp debug blocks
  (proc codes:
  `"​​log​​ %s",
  "​​breakpoint​​",
  "​​error​​ %s",
  "​​warn​​ %s"` - note: they all have ZWSPs)
- [x] Detection for `<is_compiled>` and `<is_turbowarp>` and `<is_forkphorus>` booleans

### Adding/removing blocks

- [x] Add block to sprite
- [x] Duplicating (single) block
- [x] Attach block
- [x] Duplicating blockchain
- [x] Slot above (if possible - raise error if not)
- [x] Attach blockchain
- [x] Delete block
- [x] Delete blockchain
- [x] Add/edit inputs
- [x] Add/edit fields
- [x] Add mutation
- [x] Add comment
- [x] Get comment

## Mutation

- [ ] Proc code builder
- [ ] get type of argument (bool/str) inside argument class
- [ ] to/from json for args?

## Sprite

### Finding ID components

- [x] Find var/list/broadcast
- [x] Find block/prim
- [ ] Add costume/sound
- [ ] Add var/list/broadcast
- [ ] Add arbitrary block/blockchain
- [ ] Asset count
- [ ] Obfuscation
- [ ] Var/list/broadcast/block/comment/whole id list (like `_EnumWrapper.all_of`)
- [ ] Get custom blocks list

## Vars/lists/broadcasts

- [ ]

## Monitors

- [ ] Get relevant var/list if applicable
- [ ] Generate from block

## Assets

- [x] Download assets
- [ ] Upload asset
- [ ] Load from file (auto-detect type)

## Pallet

- [ ] Add all block defaults (like sbuild.py)
- [ ] Actions (objects that behave like blocks but add multiple blocks - e.g. a 'superjoin' block that you can use to
  join more than 2 strings with one block (by actually building multiple join blocks))
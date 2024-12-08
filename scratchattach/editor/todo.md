# Things to add to scratchattach.editor (sbeditor v2)

## All

- [ ] Docstrings
- [ ] Dealing with stuff from the backpack (it's in a weird format): This may require a whole seperate module
- [ ] Getter functions (`@property`) instead of directly editing attrs (make them protected attrs)
- [ ] Check if whitespace chars break IDs
- [ ] Maybe blockchain should be renamed to 'script'
- [ ] Perhaps use sprites as blockchain wrappers due to their existing utility (loading of local globals etc)

## Project

- [ ] Asset list
- [ ] Obfuscation
- [ ] Detection for twconfig
- [ ] Edit twconfig
- [ ] Find targets

## Block

### Finding blocks/attrs

- [ ] Top level block (stack parent)
- [ ] Previous chain
- [ ] Attached chain
- [ ] Complete chain
- [ ] Block shape attr aka stack type (Stack/hat/c-mouth/end/reporter/boolean detection)
- [ ] `can_next` property
- [ ] `is_input` property: Check if block is an input obscurer
- [ ] `parent_input` property: Get input that this block obscures
- [ ] `block_tree` old 'subtree' property: Get the 'ast' of this blockchain (a tree structure, not just a list)
- [ ] `children` property - list of all blocks with this block as a parent (next block + any input obscurers)
- [ ] Detection for scratch addons debug blocks
  (proc codes:
  `"​​log​​ %s",
  "​​breakpoint​​",
  "​​error​​ %s",
  "​​warn​​ %s"` - note: they all have ZWSPs)
- [ ] Detection for `<is_compiled>` and `<is_turbowarp>` and `<is_forkphorus>` booleans

### Adding/removing blocks

- [ ] Duplicating (single) block
- [ ] Duplicating blockchain
- [ ] Attach block
- [ ] Slot above (if possible - raise error if not)
- [ ] Attach blockchain
- [ ] Delete block
- [ ] Delete blockchain
- [ ] Add/edit inputs
- [ ] Add/edit fields
- [ ] Add mutation
- [ ] Add comment

## Mutation

- [ ] Proc code builder

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

## Pallete

- [ ] Add all block defaults (like sbuild.py)
- [ ] Actions (objects that behave like blocks but add multiple blocks - e.g. a 'superjoin' block that you can use to
  join more than 2 strings with one block (by actually building multiple join blocks))
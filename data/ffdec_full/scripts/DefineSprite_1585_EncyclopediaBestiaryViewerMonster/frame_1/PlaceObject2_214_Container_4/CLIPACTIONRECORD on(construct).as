on(construct){
   while(true)
   {
      if(false)
      {
         if(!(0x28C85113 & 0x28C85113))
         {
            break;
         }
      }
      else
      {
         §§push("\x03");
      }
      if(ord(§§pop()))
      {
         backgroundRenderer = "UI_EncyclopediaLootBackground";
         set("\x16\x10\x12","UI_EncyclopediaLootBorder");
         dragAndDrop = false;
         enabled = true;
         §§push("\x18\x07\x0e");
         §§push(false);
         if(!(getTimer() + 1))
         {
            §§pop() implements ;
            §§goto(addr15b41);
         }
      }
      set(§§pop(),§§pop());
      break;
   }
   highlightRenderer = "";
   id = 0;
   margin = 2;
   set("\x1a\x1e\b",false);
   styleName = "default";
   addr15b41:
}

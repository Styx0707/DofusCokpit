on(construct){
   while(true)
   {
      if(!(0x14AEAAD5 & 0x14AEAAD5))
      {
         if(!(0x14AEAAD5 & 0x14AEAAD5))
         {
            break;
         }
      }
      else
      {
         §§push("\b");
      }
      if(!ord(§§pop()))
      {
         break;
      }
      backgroundRenderer = "UI_InventoryContainerBackground";
      set("\x16\x10\x12","");
      dragAndDrop = true;
      enabled = true;
      set("\x18\x07\x0e",true);
      highlightRenderer = "UI_InventoryContainerHighlight";
      §§push("id");
      §§push(1);
      if(false)
      {
         setProperty(§§pop(), _X, §§pop());
      }
      else
      {
         addr0889:
         set(§§pop(),§§pop());
         margin = 2;
         set("\x1a\x1e\b",false);
         styleName = "default";
      }
      return;
   }
   §§goto(addr0889);
}

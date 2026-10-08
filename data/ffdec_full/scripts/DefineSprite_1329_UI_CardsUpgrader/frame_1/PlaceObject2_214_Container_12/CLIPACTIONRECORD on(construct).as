on(construct){
   while(true)
   {
      if(!ord("\x07"))
      {
         if(!(0x051FF98C & 0x051FF98C))
         {
            break;
         }
      }
      else
      {
         §§push(8127977);
      }
      if(§§pop())
      {
         backgroundRenderer = "UI_CardGridBackground";
         set("\x16\x10\x12","");
         dragAndDrop = true;
         enabled = true;
         §§push("\x18\x07\x0e");
         §§push(true);
         if(!ord("\t"))
         {
            §§pop() implements ;
         }
         set(§§pop(),§§pop());
         highlightRenderer = "UI_CardGridHighlight";
         id = 1;
         margin = 2;
         set("\x1a\x1e\b",true);
         §§push("styleName");
         §§push("InventoryGridContainer");
         if(!(getTimer() + 1))
         {
            startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
            §§goto(addr70a6);
         }
      }
      set(§§pop(),§§pop());
      break;
   }
   addr70a6:
}

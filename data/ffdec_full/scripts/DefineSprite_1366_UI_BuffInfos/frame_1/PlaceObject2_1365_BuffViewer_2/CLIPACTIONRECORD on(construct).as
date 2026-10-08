on(construct){
   while(true)
   {
      if(false)
      {
         if(!ord("\x05"))
         {
            break;
         }
      }
      else
      {
         §§push(false);
      }
      if(!§§pop())
      {
         cellRenderer = "ItemViewerItem";
         enabled = true;
         multipleSelection = false;
         rowHeight = 20;
         §§push("styleName");
         §§push("none");
         if(!getTimer())
         {
            startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
            §§goto(addr3a387);
         }
      }
      set(§§pop(),§§pop());
      break;
   }
   set("\x16\b\t",false);
   set("\x17\x05\x15",false);
   addr3a387:
}
